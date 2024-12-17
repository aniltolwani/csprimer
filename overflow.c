// TODO: in this program, we are going to cauase a simple stackoverflow
// If we can also print out the stack at the current moment
// try to understand what the addresses are, what are the physical memory, etc.

#include <stdio.h>
#include <pthread.h>
#include <sys/resource.h>
#include <unistd.h>

void* initial_frame_address = NULL;



int fib(int n){
    if (!initial_frame_address){
        initial_frame_address = &n;
    }
    if (n % 1000 == 0){
        printf("Depth: %d, frame_address: %p. Thus far, we have used %ld bytes\n", n, &n, (long)initial_frame_address - (long)&n);
        printf("\nPaused at depth %d. PID: %d\n", n, getpid());
        printf("Run in another terminal: vmmap %d\n", getpid());
        sleep(5);  // Give us time to run vmmap
    }
    if (n == -200000) return n;
    return (fib(n - 1));
}

int main(){
    printf("Size of pointer: %lu bytes\n", sizeof(void*));
    printf("Size of int: %lu bytes\n", sizeof(int));
    
    // Initial pthread stack size
    size_t stacksize;
    pthread_attr_t attr;
    pthread_attr_init(&attr);
    pthread_attr_getstacksize(&attr, &stacksize);
    printf("Initial thread stack size: %zu bytes\n", stacksize);
    pthread_attr_destroy(&attr);
    
    // Actual stack limit
    struct rlimit rlim;

    if (getrlimit(RLIMIT_STACK, &rlim) == 0) {
        printf("Actual stack limit: %llu bytes\n", rlim.rlim_cur);
    }
    
    int a = fib(0);
    printf("res reached");
}