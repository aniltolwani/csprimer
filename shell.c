// """
// Let's implement a basic shell in C.

// No need to be POSIX-compliant, but let's figure out the basics.

// It should:
//     - DONErun in an infinite loop
//     - DONE basic things (touch, stat, ls, etc) (just call the programs after CLI parsing)
//     - DONE quit
//     - handle signals i.e. ctrl-c, ctrl-d (SIGINT, SIGTERM, etc)
//     - DONE should be forwarded into the child process
//         - i.e. if you do sleep and ctrl-c, the shell should NOT exit -- only the sleep process should exit
//     - Don't handle strings. just tokenize on spaces and tabs.
// """
// TODO: 
// - parse until multiple commands and handle them iteratively
// - use pipe and dup2 to handle changing the stdout of first command -> second
// - setup the parser to handle and take care of multiple args together
// Plan:
    // 1. parse the number of pipes using a copied string and strsep
    // 2. Run parse command on each one... maybe store them in an array of pointers to pointers.. i.e. char** [10]
    // 3. Run all of them... 


#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h> // fork, execvp, and sleep
#include <sys/wait.h>
volatile pid_t child_pid = 0;

void handle_signal(int sig){
    if (child_pid != 0){
        printf("Signal %d received\n in PID: %d\n", sig, child_pid);
        kill(child_pid, sig);
    }
    else {
        printf("No child process running\n");
        printf("shell> ");
        fflush(stdout);
    }
}

char** parse_command(char *command){
    // printf("Getting passed into parse_command: %s\n", command);
    char* temp = strdup(command);
    // tokenize and get the command
    // first, let's get a count for malloc
    int count = 0;
    char* token = strtok(temp, " \t");
    while (token){
        count += 1;
        token = strtok(NULL, " \t");
    }
    free(temp);

    char** args = malloc((count + 1) * sizeof(char*));
    token = strtok(command, " \t");
    int i = 0;
    while (token){
        args[i] = token;
        token = strtok(NULL, " \t");
        i++;
    }
    args[i] = NULL;
    return args;
}

int main(int argc, char **argv) {
    
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);
    // infinite loop
    while (1) {
        printf("shell> ");
        fflush(stdout);

        // get the input from the user
        char *line = NULL;
        size_t buf_len = 0;
        size_t chars_read = getline(&line, &buf_len, stdin);
        
        // handle EOF / ctrl-d
        if (chars_read == EOF){
            printf("Exiting shell\n");
            free(line);
            break;
        }
        // remove the newline
        if (chars_read > 0 && line[chars_read - 1] == '\n'){
            line[chars_read - 1] = '\0';
            chars_read--;  // adjust the count since we removed a character
        }
        
        printf("You said: %s which was %zu characters long from a BUFFER of %zu\n", line, chars_read, buf_len);
        // split into two commands (we will extend this later)
        int pipe_count = 0;
        char *temp_line = strdup(line);
        char* token = strtok(temp_line, "|");
        while (token){
            pipe_count += 1;
            token = strtok(NULL, "|");
        }
        printf("Pipe count is: %d", pipe_count);
        free(temp_line);
        // // TODO: this seems suspect, but what I essentially want is somethign close to a 3d char array -- 1-10 piped arguments, each argument is an array of strings (which is an array of st)
        char** args_[10];
        char* commands[10];
        token = strtok(line, "|");
        for (int i = 0; i < pipe_count; i++ ){
            // args_[i] = parse_command(token);
            commands[i] = token;
            token = strtok(NULL, "|");
        }

        for (int i = 0; i < pipe_count; i++ ){
            args_[i] = parse_command(commands[i]);
        }
        // this is just an array of file descriptiors that we will populate
        int pip_fd[pipe_count][2];
        pid_t child_pids[pipe_count];
        //  0 -> read; 1 -> write
        pipe(pip_fd[0]);
        
        // first command here
        child_pids[0] = fork();
        if (child_pids[0] == 0){ // write only pipe
            dup2(pip_fd[0][1], STDOUT_FILENO);
            // stop the read. TODO: Why do, we need to stop the read? can't we just keep it open?
            close(pip_fd[0][0]);
            close(pip_fd[0][1]);
            execvp(args_[0][0], args_[0]);
            perror("execvp failed if we get here");
        }
        // after the write only pipe is done, we can close it in the parent
        close(pip_fd[0][1]);

        for (int i = 1; i < pipe_count-1; i ++ ){
            pipe(pip_fd[i]);
            child_pids[i] = fork(); 
            if (child_pids[i] == 0){ // read and write pipe
                // let's not close anything here..
                // read from the previous pipe and write to the current
                dup2(pip_fd[i-1][0], STDIN_FILENO);
                dup2(pip_fd[i][1], STDOUT_FILENO);
                // now, we need to close read of prev and r+w of curr
                close(pip_fd[i-1][0]);
                close(pip_fd[i][0]);
                close(pip_fd[i][1]);
                execvp(args_[i][0], args_[i]);
                perror("assuming this is still an error");
            }
            // now, we are done with this. we can close the read for the previous and the write for the current.
            close(pip_fd[i-1][0]);
            close(pip_fd[i][1]);
        }

        // last command here, no pipe needed 
        child_pids[pipe_count-1] = fork();
        if (child_pids[pipe_count-1] == 0){ // read only pipe
            // stop the write
            dup2(pip_fd[pipe_count-2][0], STDIN_FILENO);
            // do we need to close the write end here?
            close(pip_fd[pipe_count-2][0]);
            execvp(args_[pipe_count-1][0], args_[pipe_count-1]);
            perror("execvp failed if we get here");
        }
        // close the final read end since we are done using it.
        close(pip_fd[pipe_count-2][0]);

        for (int i = 0; i < pipe_count; i++){
            waitpid(child_pids[i], NULL, 0);
        }

        free(line);
    }
    return 0;
}