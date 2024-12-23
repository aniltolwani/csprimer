// # write a program that writes 1 MB to a file
// # see how much that file takes up on disk
// # if this particular byte causes the file to take up more space,
// # log it!


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#define ONE_MEG 1 << 20

long get_file_size(char *f1){
    struct stat st;
    stat(f1, &st);
    return st.st_size;
}

long get_block_size(char *f1){
    struct stat st;
    stat(f1, &st);
    return st.st_blocks;
}

int main() {
    char byte = 'a';
    int fd = open("test.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd == -1) {
        perror("Error opening file");
        return 1;
    }
    long num_blocks = 0;

    for (int i = 0; i < 10000; i++) {
        if (write(fd, &byte, 1) != 1) {
            perror("Write failed");
            close(fd);
            return 1;
        }
        long fs = get_file_size("test.txt");
        long bs = get_block_size("test.txt");
        printf("Iteration %d. Block Size: %ld. File Size: %ld.\n", i, bs, fs);
        if (num_blocks != bs){
            // printf("Iteration %d. Block Size: %ld. File Size: %ld.\n", i, bs, fs);
            num_blocks = bs;
        }
    }
    
    close(fd);
    return 0;
}