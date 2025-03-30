#include <stdio.h>
#include <stdlib.h>

#include "cputime.h"
#include <pthread.h>
void merge(int *arr, int n, int mid) {
  int left = 0, right = mid, i;
  int *x = malloc(n * sizeof(int));
  // copy the ith item from either the left or right part
  for (i = 0; i < n; i++) {
    if (right == n)
      x[i] = arr[left++];
    else if (left == mid)
      x[i] = arr[right++];
    else if (arr[right] < arr[left])
      x[i] = arr[right++];
    else
      x[i] = arr[left++];
  }
  // transfer from temporary array back to given one
  for (i = 0; i < n; i++)
    arr[i] = x[i];
  free(x);
}
typedef struct {
    int *arr;
    int n;
} msort_args;


void* msort(void* arg) {
  msort_args* args = (msort_args*)arg;
  int n = args->n;
  int* arr = args->arr;
  if (n < 2)
    return NULL;
  int mid = n / 2;
  pthread_t p1, p2;
  msort_args args1 = {arr, mid};
  msort_args args2 = {arr + mid, n - mid};
  msort(&args1);
  msort(&args2);
  merge(arr, n, mid);
  return NULL;
}

int main () {
  int n = 1 << 24;
  int *arr = malloc(n * sizeof(int));
  // populate array with n many random integers
  srand(1234);
  for (int i = 0; i < n; i++)
    arr[i] = rand();

  fprintf(stderr, "Sorting %d random integers\n", n);

  // actually sort, and time cpu use
  struct profile_times t;
  int num_threads = 8;
  pthread_t threads[num_threads];
  //args array
  msort_args args[num_threads];
  int seg = n / num_threads;
  profile_start(&t);
  for (int i = 0; i < num_threads; i++) {
    // first param: the split array to sort
    // second param: the size of the split array
    // we need to segment arr into num_threads many segments
    // the first segment is from 0 to n / num_threads
    // the second segment is from n / num_threads to 2 * n / num_threads
    // the third segment is from 2 * n / num_threads to 3 * n / num_threads
    // we need to blanket initialize then cut it
    // for the last segment, it may not be of size seg
    // so we need to check if it is the last segment
    int curr_segment_start = i * seg;
    int curr_size = seg;
    if (i == num_threads - 1) {
      curr_size = n - curr_segment_start;
    }
    // copy the array
    args[i].arr = arr + curr_segment_start;
    args[i].n = curr_size;
    pthread_create(&threads[i], NULL, msort, &args[i]);
  }

  for (int i = 0; i < num_threads; i++) {
    pthread_join(threads[i], NULL);  
  }
  // merge all the segments iteratively
  for (int i = 0; i < num_threads; i++) {
    // merge needs 3 params
    // arr: always just arr
    // n: start_idx + seg_size
    // mid: start_idx since everything before mid is already sorted
    // importantly, we only need to merge: i > 0
    // for the last segment, we need to update seg size to be n - start_idx
    int start_idx = i * seg;
    int seg_size = seg;
    if (i == num_threads - 1) {
      seg_size = n - start_idx;
    }
    if (i > 0) {
      merge(arr, start_idx + seg_size, start_idx);
    }
  }

  profile_log(&t);

  // assert that the output is sorted
  for (int i = 0; i < n - 1; i++)
    if (arr[i] > arr[i + 1]) {
      printf("error: arr[%d] = %d > arr[%d] = %d", i, arr[i], i + 1,
             arr[i + 1]);
      return 1;
    }
    return 0;
}
