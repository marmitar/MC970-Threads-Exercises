#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>


// Print hello world from a thread
static void *printHello(void *threadId) {
    unsigned tid = (unsigned) (uintptr_t) threadId;

    printf("Hello Worlds from thread #%u!\n", tid);

    // Pause for 3 seconds
    sleep(3);

    printf("Goodbye from thread #%u!\n", tid);

    return NULL;
}

int main(void) {
    pthread_t id[NUM_THREADS];

    for (unsigned t = 0; t < NUM_THREADS; t++) {
        printf("Creating thread #%u\n", t);
        int rv = pthread_create(&id[t], NULL, printHello, (void *) (uintptr_t) t);
        if (rv != 0) {
            return EXIT_FAILURE;
        }
    }

    // Wait for all threads to finish
    for (unsigned t = 0; t < NUM_THREADS; t++) {
        pthread_join(id[t], NULL);
    }

    return EXIT_SUCCESS;
}
