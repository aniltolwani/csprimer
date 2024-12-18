#include <stdio.h>
#include <string.h>

int main() {
    char *args[10];
    char str[] = "ls";
    args[0] = str;
    args[1] = NULL;

    printf("Before strcmp: args[0]='%s' args[1]='%s'\n", args[0], args[1]);
    if (strcmp(args[0], "exit") == 0){
        printf("args[0] is 'exit'\n");
    }
    printf("After strcmp: args[0]='%s' args[1]='%s'\n", args[0], args[1]);
    return 0;
}