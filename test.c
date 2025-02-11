#include <stdio.h>
#include <stdlib.h>

int main() {
    printf("File quick.c has been renamed to quicksort.c\n");
    fflush(stdout);  // 👈 Force immediate output
    while (1) {
        // Keep the process alive to detect further changes
    }
    return 0;
}