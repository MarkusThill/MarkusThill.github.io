/*
 * Index of an isolated set bit in a 64bit word, using the de Bruijn word of
 * order six that the enumeration above produces as its smallest solution.
 ****/
#include <stdio.h>
#include <stdint.h>

static const uint64_t DEBRUIJN64 = 0x0218a392cd3d5dbfULL;
static int index64[64];

static void init_table(void) {
  for (int k = 0; k < 64; k++)
    index64[(DEBRUIJN64 << k) >> 58] = k;
}

static int bit_pos(uint64_t x) {   /* x must have exactly one bit set */
  return index64[(x * DEBRUIJN64) >> 58];
}

int main(void) {
  init_table();
  for (int k = 0; k < 64; k++)
    if (bit_pos((uint64_t)1 << k) != k) {
      printf("failed at %d\n", k);
      return 1;
    }
  printf("all 64 positions correct\n");
  return 0;
}
