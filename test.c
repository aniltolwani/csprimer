#include <stdlib.h>
#include <string.h>

int main() {
    int* x = malloc(sizeof(int));
    *x = 5;
    free(x);
    
    char* y = malloc(6);  // 5 + null terminator
    strcpy(y, "hello");
    free(y);
    return 0;
}