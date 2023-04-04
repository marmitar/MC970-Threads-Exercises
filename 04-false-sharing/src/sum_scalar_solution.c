/*
 * sum_scalar.c - A simple parallel sum program to sum a
 * series of scalars
 */

#include <limits.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>


void *sum(void *p);

// global shared variables
unsigned long int psum[MAXTHREADS]; // partial sum computed by each thread
unsigned long int sumtotal = 0;
unsigned long int n;
unsigned long numthreads;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

int main(int argc, char **argv) {
    struct timeval start, end;
    gettimeofday(&start, NULL); /* start timing */

    if (argc != 3) {
        printf("Usage: %s <n> <numthreads>\n", argv[0]);
        return 1;
    }

    n = strtoul(argv[1], NULL, 10);
    numthreads = strtoul(argv[2], NULL, 10);

    if (numthreads < 1 || numthreads > MAXTHREADS) {
        fprintf(stderr, "Invalid number of threads: %lu\n", numthreads);
        return EXIT_FAILURE;
    }

    pthread_t tid[MAXTHREADS];
    unsigned long myid[MAXTHREADS];
    for (unsigned long i = 0; i < numthreads; i++) {
        myid[i] = i;
        psum[i] = 0L;
        int rv = pthread_create(&tid[i], NULL, sum, &myid[i]);
        if (rv != 0) {
            return EXIT_FAILURE;
        }
    }

    for (unsigned long i = 0; i < numthreads; i++) {
        pthread_join(tid[i], NULL);
    }

    pthread_mutex_destroy(&mutex);
    gettimeofday(&end, NULL); /* end timing */
    long spent = (end.tv_sec * 1000000 + end.tv_usec) -
                             (start.tv_sec * 1000000 + start.tv_usec);

    printf("sum = %lu\ntime_us = %ld\n", sumtotal, spent);

    return 0;
}

#ifdef __clang__
// clang currently don't have the NOIPA attribute, so we must disable
// any kind of optimizations with OPTNONE and NOINLINE
#define _disable_optimizations \
    __attribute__((noinline, optnone))
#else
// GCC has NOIPA, so only the function call may not be optimized
#define _disable_optimizations \
    __attribute__((noipa))
#endif

static _disable_optimizations
/** The step for the `sum` function, disabling loop optimizations. */
unsigned long step(void) {
    return 2;
}

void *sum(void *p) {
    unsigned long myid = *(unsigned long *) p;
    unsigned long start = (myid * n) / numthreads;
    unsigned long end = ((myid + 1) * n) / numthreads;

    for (unsigned long i = start; i < end; i++) {
        psum[myid] += step();
    }

    int rv = pthread_mutex_lock(&mutex);
    if (rv == 0) {
        sumtotal += psum[myid];
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}
