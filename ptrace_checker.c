#include <sys/ptrace.h>
#include <stdlib.h>

void anti_debug() {
    if (ptrace(PTRACE_TRACEME, 0, NULL, 0) == -1) {
        printf("DEBUG DETECTED!");
        exit(1);
    }
}
