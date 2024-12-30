#define _GNU_SOURCE
#include <linux/futex.h>
#include <sys/time.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <errno.h>
#include <pthread.h>
#include <unistd.h>

int futex_var = 0;

// Function to invoke the futex syscall
static int futex(int *uaddr, int futex_op, int val, const struct timespec *timeout, int *uaddr2, int val3) {
    return syscall(SYS_futex, uaddr, futex_op, val, timeout, uaddr2, val3);
}

// Waker thread function
void *waker_thread(void *arg) {
    int iterations = *(int *)arg;
    for (int i = 0; i < iterations; i++) {
        futex_var = 1;
        if (futex(&futex_var, FUTEX_WAKE, 1, NULL, NULL, 0) == -1) {
            perror("futex_wake failed");
            exit(EXIT_FAILURE);
        }
        usleep(100); // Small delay to simulate realistic wake-up timing
    }
    return NULL;
}

// Benchmarking function for futex
void benchmark_futex(int iterations) {
    pthread_t thread;
    if (pthread_create(&thread, NULL, waker_thread, &iterations) != 0) {
        perror("pthread_create failed");
        exit(EXIT_FAILURE);
    }

    struct timespec ts = {0, 1000000}; // 1 ms timeout

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < iterations; i++) {
        futex_var = 0; // Reset futex_var before waiting
        if (futex(&futex_var, FUTEX_WAIT, 0, &ts, NULL, 0) == -1 && errno != EAGAIN) {
            //perror("futex_wait failed");
	    continue;
            exit(EXIT_FAILURE);
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    pthread_join(thread, NULL);

    double elapsed_time = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    printf("Futex benchmark completed: %d iterations in %.6f seconds.\n", iterations, elapsed_time);
    printf("Average Futex syscall based on %d iterations is %.6f seconds.\n",iterations,elapsed_time/iterations);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <iterations>\n", argv[0]);
        return EXIT_FAILURE;
    }

    int iterations = atoi(argv[1]);
    if (iterations <= 0) {
        fprintf(stderr, "Iterations must be a positive integer.\n");
        return EXIT_FAILURE;
    }

    printf("Starting futex benchmark with %d iterations...\n", iterations);
    benchmark_futex(iterations);

    return EXIT_SUCCESS;
}
