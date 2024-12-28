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
    printf("Getting passed into parse_command: %s\n", command);
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
    for (int i = 0; i < count; i ++){
        printf("Arg %d: %s\n", i, args[i]);
    }
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
        
        printf("You said: %s which was %zu characters long from a buffer of %zu\n", line, chars_read, buf_len);

        // split into two commands (we will extend this later)
        char *command1 = strtok(line, "|");
        char* temp1 = strdup(command1);
        char *command2 = strtok(NULL, "|");
        char* temp2 = strdup(command2);

        char** args1 = parse_command(temp1);
        char** args2 = parse_command(temp2);
        
        int pip_fd[2];
        //  0 -> read; 1 -> write
        pipe(pip_fd);
        
        pid_t pid1 = fork();
        if (pid1 == 0){
            // stop the read
            close(pip_fd[0]);
            // pipe it to write
            dup2(pip_fd[1], STDOUT_FILENO);
            // close the write since we have duped it. TODO: understand this better. 
            close(pip_fd[1]);
            execvp(args1[0], args1);
            perror("execvp failed if we get here");
        }

        pid_t pid2 = fork();
        if (pid2 == 0){
            // stop the write
            close(pip_fd[1]);
            // pipe it to read
            dup2(pip_fd[0], STDIN_FILENO);
            // close the read since we have used it.
            close(pip_fd[0]);
            execvp(args2[0], args2);
            perror("execvp failed if we get here");
        }
        close(pip_fd[0]);
        close(pip_fd[1]);
        waitpid(pid1, NULL, 0);
        waitpid(pid2, NULL, 0);
        free(line);
    }
    return 0;
}