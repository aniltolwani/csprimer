#include <stdlib.h>
#include <unistd.h>
#include <sys/time.h>
#include <stdio.h>
#include <sys/resource.h>
#include <unistd.h>

#define SLEEP_SEC 3
#define NUM_MULS 100000000
#define NUM_MALLOCS 100000
#define MALLOC_SIZE 1000

// TODO define this struct
struct profile_times {
  struct timeval start;
  struct timeval end;
  struct rusage start_r;
  struct rusage end_r;
};

// TODO populate the given struct with starting information
void profile_start(struct profile_times *t) {
  gettimeofday(&t->start, NULL);
  getrusage(0, &t->start_r);
}

double diff_timeval(struct timeval v1, struct timeval v2){
  double diff = (
    v2.tv_sec - v1.tv_sec
  ) + (v2.tv_usec - v1.tv_usec) / 1000000.0;
  return diff;
}
// TODO given starting information, compute and log differences to now
void profile_log(struct profile_times *t) {
  gettimeofday(&t-> end, NULL);
  getrusage(0,&t->end_r);
  double real_diff = diff_timeval(t->start, t->end);
  double user_time = diff_timeval(t->start_r.ru_utime, t->end_r.ru_utime);
  double syscall_time = diff_timeval(t->start_r.ru_stime, t->end_r.ru_stime);
  printf("Clock time: %f; User Time: %f, Sys Time: %f\n", real_diff, user_time, syscall_time);
}

int main(int argc, char *argv[]) {
  pid_t pid = getpid();
  printf("PID: %d\n\n", pid );
  struct profile_times t;

  // TODO profile doing a bunch of floating point muls
  printf("Floating Point Muls\n");
  float x = 1.0;
  profile_start(&t);
  for (int i = 0; i < NUM_MULS; i++)
    x *= 1.1;
  profile_log(&t);

  // TODO profile doing a bunch of mallocs
  printf("Mallocs\n");
  profile_start(&t);
  void *p;
  for (int i = 0; i < NUM_MALLOCS; i++)
    p = malloc(MALLOC_SIZE);
  profile_log(&t);

  printf("Sleep\n");
  // TODO profile sleeping
  profile_start(&t);
  sleep(SLEEP_SEC);
  profile_log(&t);
}
