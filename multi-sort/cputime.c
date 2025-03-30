#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

#include "cputime.h"

// REMOVE the getcpuid function entirely
/*
unsigned int getcpuid() {
  unsigned reg[4];
  __cpuid_count(1, 0, reg[0], reg[1], reg[2], reg[3]);
  return reg[1] >> 24;
}
*/

// ADD Helper function to convert timespec to microseconds
static uint64_t timespec_to_usec(const struct timespec *ts) {
  return (uint64_t)ts->tv_sec * 1000000 + ts->tv_nsec / 1000;
}

// ADD Helper function to convert timeval to microseconds
static uint64_t timeval_to_usec(const struct timeval *tv) {
  return (uint64_t)tv->tv_sec * 1000000 + tv->tv_usec;
}


// REWRITE profile_start
void profile_start(struct profile_times *t) {
  if (!t) return;

  struct timespec wall_ts;
  struct rusage usage;

  // Get starting wall-clock time
  if (clock_gettime(CLOCK_MONOTONIC, &wall_ts) == -1) {
    perror("clock_gettime");
    memset(t, 0, sizeof(*t)); // Zero out times on error
    return;
  }

  // Get starting CPU times
  if (getrusage(RUSAGE_SELF, &usage) == -1) {
    perror("getrusage");
    memset(t, 0, sizeof(*t)); // Zero out times on error
    return;
  }

  // Store starting times in microseconds
  t->wall_clock_usec = timespec_to_usec(&wall_ts);
  t->user_cpu_usec = timeval_to_usec(&usage.ru_utime);
  t->kernel_cpu_usec = timeval_to_usec(&usage.ru_stime);
}

// REWRITE profile_log - Now calculates and stores durations in t
void profile_log(struct profile_times *t) {
  if (!t) return;

  struct timespec wall_ts_end;
  struct rusage usage_end;

  // Keep copies of the original start times
  uint64_t start_wall_usec = t->wall_clock_usec;
  uint64_t start_user_usec = t->user_cpu_usec;
  uint64_t start_kernel_usec = t->kernel_cpu_usec;

  // Get ending wall-clock time
  if (clock_gettime(CLOCK_MONOTONIC, &wall_ts_end) == -1) {
    perror("clock_gettime");
    // On error, store 0 duration
    t->wall_clock_usec = 0;
    t->user_cpu_usec = 0;
    t->kernel_cpu_usec = 0;
    return; // Or handle error differently
  }

  // Get ending CPU times
  if (getrusage(RUSAGE_SELF, &usage_end) == -1) {
    perror("getrusage");
    // On error, store 0 duration
    t->wall_clock_usec = 0;
    t->user_cpu_usec = 0;
    t->kernel_cpu_usec = 0;
    return; // Or handle error differently
  }

  // Calculate durations in microseconds and update the struct t
  // Note: This overwrites the start times in t with the durations.
  t->wall_clock_usec = timespec_to_usec(&wall_ts_end) - start_wall_usec;
  t->user_cpu_usec = timeval_to_usec(&usage_end.ru_utime) - start_user_usec;
  t->kernel_cpu_usec = timeval_to_usec(&usage_end.ru_stime) - start_kernel_usec;

  // UPDATE fprintf to print the calculated durations (stored in t)
  // Removed getcpuid() call. Using -1 as a placeholder for CPU ID.
  fprintf(stderr, "[pid %d] real: %.03fs user: %0.03fs sys: %0.03fs\n",
          getpid(),
          t->wall_clock_usec / 1000000.0,
          t->user_cpu_usec / 1000000.0,
          t->kernel_cpu_usec / 1000000.0);
} 