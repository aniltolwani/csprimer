#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <sys/wait.h>

typedef struct {
    pid_t pid;
    pid_t pgid;      // Process group ID
    char state;      // 'R'unning, 'S'topped, 'B'ackground
    char name[50];
} Job;

Job jobs[10];
int job_count = 0;
pid_t shell_pgid;    // Our shell's process group

// Initialize terminal settings
void init_shell() {
    // Put ourselves in our own process group
    shell_pgid = getpid();
    setpgid(shell_pgid, shell_pgid);
    
    // Take control of the terminal
    tcsetpgrp(STDIN_FILENO, shell_pgid);
}

void spawn_process(const char* name, int background) {
    pid_t pid = fork();
    
    if (pid == 0) {  // Child process
        // Create new process group for the child
        setpgid(0, 0);
        
        // If foreground process, give it terminal control
        if (!background) {
            tcsetpgrp(STDIN_FILENO, getpgrp());
        }
        
        // Simple simulation program
        while(1) {
            printf("[%s] working... (PID: %d, PGID: %d)\n", 
                   name, getpid(), getpgrp());
            sleep(1);
        }
    } else {  // Parent process
        // Store job info
        jobs[job_count].pid = pid;
        jobs[job_count].pgid = pid;  // New process group
        jobs[job_count].state = background ? 'B' : 'R';
        strncpy(jobs[job_count].name, name, 49);
        job_count++;
        
        if (!background) {
            // Wait for foreground process
            int status;
            waitpid(pid, &status, WUNTRACED);
            
            // Take back terminal control
            tcsetpgrp(STDIN_FILENO, shell_pgid);
        }
    }
}

void make_foreground(int job_id) {
    if (job_id >= job_count) return;
    
    Job *job = &jobs[job_id];
    
    // Give the process group terminal control
    tcsetpgrp(STDIN_FILENO, job->pgid);
    
    // Continue the process if it was stopped
    if (job->state == 'S' || job->state == 'B') {
        kill(-job->pgid, SIGCONT);  // Note the minus sign!
    }
    
    job->state = 'R';
    
    // Wait for it to stop or terminate
    int status;
    waitpid(job->pid, &status, WUNTRACED);
    
    // Take back terminal control
    tcsetpgrp(STDIN_FILENO, shell_pgid);
}

void make_background(int job_id) {
    if (job_id >= job_count) return;
    
    Job *job = &jobs[job_id];
    
    // Continue the process if it was stopped
    if (job->state == 'S') {
        kill(-job->pgid, SIGCONT);
    }
    
    job->state = 'B';
    printf("[%d] %s running in background\n", job_id, job->name);
}

void list_jobs() {
    printf("\nCurrent Jobs:\n");
    for(int i = 0; i < job_count; i++) {
        printf("[%d] %s (PID: %d, PGID: %d) - %c\n", 
               i, jobs[i].name, jobs[i].pid, jobs[i].pgid, jobs[i].state);
    }
}

int main() {
    init_shell();
    
    char command[50];
    printf("Enhanced Job Control System\n");
    printf("Commands: new <name>, bg <id>, fg <id>, stop <id>, continue <id>, list, quit\n");
    
    while(1) {
        printf("\n> ");
        fgets(command, 50, stdin);
        command[strlen(command)-1] = '\0';
        
        if (strncmp(command, "new ", 4) == 0) {
            // Start in foreground by default
            spawn_process(command + 4, 0);
        }
        else if (strncmp(command, "bg ", 3) == 0) {
            int id = atoi(command + 3);
            make_background(id);
        }
        else if (strncmp(command, "fg ", 3) == 0) {
            int id = atoi(command + 3);
            make_foreground(id);
        }
        else if (strncmp(command, "stop ", 5) == 0) {
            int id = atoi(command + 5);
            if (id < job_count) {
                kill(-jobs[id].pgid, SIGSTOP);  // Stop whole process group
                jobs[id].state = 'S';
            }
        }
        else if (strncmp(command, "continue ", 9) == 0) {
            int id = atoi(command + 9);
            if (id < job_count) {
                kill(-jobs[id].pgid, SIGCONT);  // Continue whole process group
                jobs[id].state = 'B';  // Continue in background
                printf("[%d] %s continued in background\n", id, jobs[id].name);
            }
        }
        else if (strcmp(command, "list") == 0) {
            list_jobs();
        }
        else if (strcmp(command, "quit") == 0) {
            for(int i = 0; i < job_count; i++) {
                kill(-jobs[i].pgid, SIGKILL);
            }
            break;
        }
    }
    
    return 0;
}