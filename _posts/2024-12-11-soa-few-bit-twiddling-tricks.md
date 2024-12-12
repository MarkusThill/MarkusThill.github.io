---
layout: post
title: A few Bit-Twiddling Tricks
modified:
categories: 
tags: [bit, twiddling, hacks, performance, speed]
description: "When working with bit-fields, there are several techniques that can significantly speed up code — beyond the inherent performance benefits that bit-fields provide for many problems. In this post, I will introduce a few bit-twiddling tricks that I occasionally use, which can be useful for a variety of tasks."
thumbnail: assets/img/bit-twiddling.webp
giscus_comments: true
featured: False
share:
date: 2024-12-11 15:16:00
---


When working with bit-fields, there are several techniques that can significantly speed up code — beyond the inherent performance benefits that bit-fields provide for many problems. In this post, I will introduce a few bit-twiddling tricks that I occasionally use, which can be useful for a variety of tasks.

## Swapping Variables with the bitwise Exclusive Or
A very common programming problem is swapping the values of two variables, $$x$$ and $$y$$. The most common approach is to introduce a temporary variable, $$z$$, as follows:

{% highlight C %}
  int x = 35;
  int y = 67;
  int z;
  z = x;
  x = y;
  y = z;
{% endhighlight %}

In practice, many compilers optimize this code and eliminate the temporary variable. However, there is also an elegant approach to perform this manually using the bitwise exclusive OR (XOR) operator:

{% highlight C %}
  int x = 35;
  int y = 67;
  x = x ^ y;  // x = 96
  y = x ^ y;  // y = 67
  x = x ^ y;  // x = 35 
{% endhighlight %}

<!--more-->

This uses the property of the exclusive or that $$x \oplus x = 0$$ and its associative and commutative property, so that for instance $$ x \oplus y \oplus x = x \oplus x \oplus y = (x \oplus x) \oplus y = 0 \oplus y = y$$. One could similarily solve the problem with (as a side note):

{% highlight C %}
 int x = 35;
 int y = 67;
 x = x - y;
 y = x + y;
 x = y - x;
{% endhighlight %}

To be precise, this method works for all Abelian groups that satisfy the properties of commutativity, associativity, the existence of an identity element, and the existence of an inverse for each element (or where each element is its own inverse).


## Shifting and Rotating
Commonly used bitwise operations include the shifting operations. There are two main types in C: the right shift `>>` and the left shift `<<`. In C, the right shift is typically an arithmetic operation, shifting all bits to the right while preserving the sign (padding with the most significant bit). The left shift, on the other hand, pads the least significant bits with zeros. However, this behavior is implementation-dependent; some compilers may perform a logical right shift, where padding is done with zeros.

In Java, the arithmetic right shift is also represented by `>>`, where the padding is done with the most significant bit to preserve the sign. Java also provides the logical right shift using `>>>`, which pads with zeros. Arithmetically, a left shift by one is equivalent to multiplying an integer by 2, while an arithmetic right shift by one corresponds to integer division by 2.

Most CPUs also support left and right rotating operations. In this case, bits that are shifted out from one side of the bit-field are wrapped around and padded on the other side. However, many high-level programming languages do not support these operations directly. With the following inline assembler code, you can also perform left and right rotations on X86_X64 platforms.


{% highlight C %}
/*
 * Rotatate 64bit variable x by y bits. Note that this is not a shift-operation but a real
 * roll-left
 ****/
static inline uint64_t rol(uint64_t x, unsigned int n) {
    __asm__ ("rolq %1, %0" : "+g" (x) : "cJ" ((unsigned char) n));
    return x;
}

/*
 * Same as rol, only rotates right instead of left.
 ****/
static inline uint64_t ror(uint64_t x , unsigned int n ) {
    __asm__ ("rorq %1, %0" : "+g" (x) : "cJ" ((unsigned char) n));
    return x;
}
{% endhighlight %}



## How to set/delete a Bit in a Bit Field
Many programmers often wonder how to set, remove, or invert a bit in a bit-field. This can be easily achieved using the bitwise OR and AND operators, as demonstrated by the following functions:


{% highlight C %}
/*
 * Sets a bit (sets it to 1)
 ****/
uint64_t setBit(uint64_t b, int bit) {
    return b | (1UL << bit);
}

/*
 * Deletes a bit (sets it to 0)
 ****/
uint64_t deleteBit(uint64_t b, int bit) {
    return b & (~(1UL << bit));
}

/*
 * Inverts a bit (sets it to 1)
 ****/
uint64_t invertBit(uint64_t b, int bit) {
    return b ^ (1UL << bit);
}
{% endhighlight %}

## Counting the set Bits in a Bit Field
If you want to count the bits in a bit-field, a naive approach might involve masking out one bit at a time and checking if it is set. However, if only a few bits are set, the following function will perform much faster. In fact, it only requires as many iterations as there are set bits in the variable. This function is designed for 64-bit values but can easily be adjusted for 32-bit or 16-bit variables.


{% highlight C %}
/*
 * Fast way to count the one-bits in a 64bit variable.
 * Only requires as many iterations as bits are set.
 ****/
int bitCount(uint64_t x) {
    const uint64_t ZERO = 0x1p0 - 1;
    int c = 0;
    while (x != ZERO) {
        x &= (x - 1);
        c++;
    }
    return c;
}
{% endhighlight %}



## Find the Position of a set Bit
Sometimes, you may want to find the position of a single set bit in a bit-field. A naive approach would involve iterating through all the bits and checking each one to see if it is set. However, this results in linear time complexity. For a 64-bit variable, you would require 64 iterations in the worst case. We can improve on this.

The following approach is similar to the divide-and-conquer strategies commonly used in many problems. First, we check which half of the bit-field contains the set bit. Then, we split that half into two parts and check which one contains the set bit, continuing this process iteratively. With this approach, we can locate the bit in logarithmic time. For a 64-bit variable, this would take just 6 iterations, which is significantly faster than the 64 iterations required by the naive method.

Note, however, that this function assumes only a single bit is set in the entire bit-field. Mathematically, this function computes the binary logarithm of a value that is a power of two.

{% highlight C %}
const uint64_t ZERO = 0x1p0 - 1;
const uint64_t B32 = 0x1p32 - 1;
const uint64_t B16 = 0x1p16 - 1;
const uint64_t B08 = 0x1p8 - 1;
const uint64_t B04 = 0x1p4 - 1;
const uint64_t B02 = 0x1p2 - 1;
const uint64_t B01 = 0x1p1 - 1;
const uint64_t B_LVL[] = {B01, B02, B04, B08, B16, B32};

/*
 * Determines the position of a single bit in a 64bit variable in logarithmic time.
 * Basically the same as the binary logarithm of a power of two.
 ****/
int bitPos(uint64_t x) {
    int bPos = 0;
    for (int i = 5; i >= 0; i--) {
        if ((x & B_LVL[i]) == ZERO) {
            int nBits = (int) B01 << i;
            x >>= nBits;
            bPos += nBits;
        }
    }
    return bPos;
}
{% endhighlight %}



## Modulo Operations for Divisors of Powers of Two
Similar to the decimal system, where a modulo operation with a divisor of 10 returns the last digit (assuming the dividend is positive), and a modulo operation with 100 returns the last two digits (and so on), a modulo operation with a binary $$(10)_2$$ (which is 2 in the decimal system) and $$(100)_2$$ (which is 4 in the decimal system) would return the last binary digit and the last two binary digits, respectively. 

Thus, a modulo operation by a power of two can be implemented efficiently and can save significant computation time when used repeatedly. For example, if you have a hash table with $$2^n$$ entries, you can easily map a hash value to an index in the table using such a modulo operation. If the hash table is accessed many millions of times, using an efficient modulo implementation can save considerable time. Note that many compilers' optimizers do not take into account the special case where the divisor is a power of two. 

A modulo function that computes $$x \, \mbox{mod} \, 2^n$$ might look like this:


{% highlight C %}
uint64_t modPow2(uint64_t x, uint64_t n) {
  return x & ((1UL << n) - 1);
}
{% endhighlight %}
