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

    for (int i = 0; i < 1048577; i++) {
        if (write(fd, &byte, 1) != 1) {
            perror("Write failed");
            close(fd);
            return 1;
        }
        long fs = get_file_size("test.txt");
        long bs = get_block_size("test.txt");
        if (num_blocks != bs){
            printf("Block Size: %ld. Allocated size: %ld. File Size: %ld. Iteration %d\n",  
                   bs, bs * 512, fs, i);
            num_blocks = bs;
        }
    }
    
    long final_fs = get_file_size("test.txt");
    long final_bs = get_block_size("test.txt");
    printf("\nFinal Status:\n");
    printf("Actual file size: %ld bytes\n", final_fs);
    printf("Allocated blocks: %ld (Total: %ld bytes)\n", final_bs, final_bs * 512);
    
    close(fd);
    return 0;
}