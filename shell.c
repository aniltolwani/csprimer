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

        // tokenize and get the command
        char *command = strtok(line, " \t");
        char *args[10];
        int i = 0;
        while (1){
            args[i] = command;
            command = strtok(NULL, " \t");
            i++;
            if (command == NULL) break;
        }
        args[i] = NULL;
        if (strcmp(args[0], "exit") == 0){
            free(line);
            break;
        }
        printf("Command: %s\n", args[0]);
        for (int j = 0; j < i + 1; j++){
            printf("Arg %d: %s\n", j, args[j]);
        }
        // just sleep for a bit to see what's going on
        child_pid = fork();
        if (child_pid == 0){
            execvp(args[0], args);
            perror("execvp failed if we get here");
        }
        else {
            waitpid(child_pid, NULL, 0);
            child_pid = 0;
        }
        free(line);
    }
    return 0;
}