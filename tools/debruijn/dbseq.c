/*
 * Enumerate all binary circular words of length 2^n whose n-windows are
 * pairwise distinct, and sum their numeric representations.
 *
 * The set of already visited windows is a single machine word as long as
 * n <= 6, so the "have I seen this window?" test is one shift and one AND.
 ****/
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>

static int n_bits;              /* window width n, between 2 and 6         */
static int n_windows;           /* 2^n windows, the vertices of the graph  */
static int window_mask;         /* 2^n - 1, cuts the shift register to n   */
static int forced_zeros_from;   /* from here on, only a 0 may be appended  */

static uint64_t used;           /* bit i is set if window i is in the walk */
static unsigned __int128 sum_of_circles;
static uint64_t n_circles, n_nodes;

static void dfs(int window, int placed, uint64_t digits) {
  n_nodes++;
  if (placed == n_windows) {    /* all windows used, the circle is complete */
    sum_of_circles += digits;
    n_circles++;
    return;
  }

  /* The last n-1 digits of every circle are the zeros that wrap around. */
  int max_digit = (placed >= forced_zeros_from) ? 0 : 1;

  for (int digit = 0; digit <= max_digit; digit++) {
    /* shift the window one position on and append the new digit */
    int next_window = ((window << 1) | digit) & window_mask;

    if (used >> next_window & 1) continue;          /* window already taken */
    used |= (uint64_t)1 << next_window;

    /* the digit dropped by the shift is the next digit of the circle */
    dfs(next_window, placed + 1,
        (digits << 1) | (uint64_t)(next_window >> (n_bits - 1)));

    used &= ~((uint64_t)1 << next_window);          /* undo when backtracking */
  }
}

/* __int128 has no printf conversion, so print it by hand. */
static void print_u128(unsigned __int128 x) {
  char buf[41];
  int i = 40;
  buf[i] = '\0';
  if (x == 0) buf[--i] = '0';
  while (x) { buf[--i] = '0' + (int)(x % 10); x /= 10; }
  fputs(buf + i, stdout);
}

int main(int argc, char **argv) {
  n_bits = (argc > 1) ? atoi(argv[1]) : 5;
  if (n_bits < 2 || n_bits > 6) { fprintf(stderr, "n must be 2..6\n"); return 1; }
  n_windows         = 1 << n_bits;
  window_mask       = n_windows - 1;
  forced_zeros_from = n_windows - n_bits + 1;
  used              = 1;        /* the all-zero window is the starting point */

  clock_t t0 = clock();
  dfs(0, 1, 0);
  double dt = (double)(clock() - t0) / CLOCKS_PER_SEC;

  printf("n=%d  circles=%llu  nodes=%llu  S=", n_bits,
         (unsigned long long)n_circles, (unsigned long long)n_nodes);
  print_u128(sum_of_circles);
  printf("  time=%.3f s\n", dt);
  return 0;
}
