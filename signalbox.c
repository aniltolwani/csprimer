// TODO: write a program which uses the current terminal size to draw a picture, and respond to resizing
// Plan:
// 1. Handle the terminal resize signal 
// 2. Print the current terminal dims when we receive a new signal
// 3. Print something that uses the new dimensions (i.e. properly resized rectangle, etc.)

#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/ioctl.h>

// percentages for rect and height
#define RECT_W .20
#define RECT_H .30

struct winsize w;

void print_rect(){
    ioctl(STDOUT_FILENO, TIOCGWINSZ, &w);
    // c truncates by default
    int rect_c_x = w.ws_row / 2;
    int rect_c_y = w.ws_col / 2;

    int start_x = rect_c_x - (RECT_W * w.ws_row);
    int end_x = start_x + (2 * RECT_W * w.ws_row);

    int start_y = rect_c_y - (RECT_H * w.ws_col);
    int end_y = start_y + (2 * RECT_H * w.ws_col);
    // Clear screen
    printf("\033[2J\033[H");

    for (int r = 0; r < w.ws_row; r ++){
        for (int c = 0; c < w.ws_col; c++){
            if (r >= start_x && r <= end_x && c >= start_y && c <= end_y){
                printf("█");
            }
            else{
                printf(" ");
            }
        }
    }

    fflush(stdout);
}

void handle_signal(int sig){
    // printf("signal %d recieved\n", sig);
    if (sig == SIGWINCH){
        print_rect();
    }
    signal(sig, SIG_DFL);
    raise(sig);
}

int main(int argc, char ** argv){
    while(1){
        signal(SIGINT, handle_signal);
        signal(SIGTERM, handle_signal);
        signal(SIGWINCH, handle_signal);        
    }
}