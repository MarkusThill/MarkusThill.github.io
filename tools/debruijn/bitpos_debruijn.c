/*
 * The de Bruijn variant of bitPos(), in the naming of the bit-twiddling post.
 * Kept separate from bitscan.c so that both posts quote code that was compiled
 * and tested exactly as printed.
 ****/
#include <stdio.h>
#include <stdint.h>

/*
 * Position of a single set bit in a 64bit variable, with one multiplication,
 * one shift and one table lookup. The constant is a de Bruijn sequence of
 * order 6: shifted by k, its topmost 6 bits differ for every k.
 ****/
const uint64_t DEBRUIJN64 = 0x0218a392cd3d5dbfULL;
int deBruijnIdx[64];

void initBitPosTable() {
    for (int k = 0; k < 64; k++) {
        deBruijnIdx[(DEBRUIJN64 << k) >> 58] = k;
    }
}

int bitPosDeBruijn(uint64_t x) {  // x must have exactly one bit set
    return deBruijnIdx[(x * DEBRUIJN64) >> 58];
}

int main(void) {
    initBitPosTable();
    for (int k = 0; k < 64; k++) {
        uint64_t x = (uint64_t)1 << k;
        if (bitPosDeBruijn(x) != k) { printf("failed at %d\n", k); return 1; }
    }
    /* the usual way to feed it: isolate the lowest set bit first */
    uint64_t v = 0xdeadbeef00000000ULL;
    printf("all 64 positions correct, lowest set bit of 0xdeadbeef00000000 is %d\n",
           bitPosDeBruijn(v & -v));
    return 0;
}
