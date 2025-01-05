---
layout: post
title: A short Implementation of Booth's Multiplication Algorithm in 6502 Assembly
modified:
categories: []
description: "I implemented a 6502 assembly routine for multiplying two one-byte integers using Booth's algorithm. While the algorithm itself wasn't difficult to implement, it took time to create a solution that fit within 40 lines of code. I also wrote a test routine to verify the multiplication, covering various predefined combinations, edge cases, and scenarios where one factor is zero."
tags: [Assembly 6502 Booth Multiplication]
giscus_comments: true
featured: False
thumbnail: assets/img/booth-algorithm-6502.webp
share: 
date: 2024-12-16 04:16:00
---
Some time ago, I had to implement a multiplication routine in 6502 assembly for two integer factors, each one byte in size, using Booth's multiplication algorithm. Implementing Booth's method itself was not particularly tricky. However, it took me some time to come up with a solution that requires only around 40 lines of code.

I also found it important to write a routine that tests the multiplication with various predefined combinations of the two factors. The tests included all edge cases, as well as cases where at least one of the factors is zero.

The code was also benchmarked [here](https://github.com/TobyLobster/multiply_test). As it turns out, it is not terribly fast (depending on the benchmark, Booth's algorithm does not always leverage its advantages), but it requires only 49 bytes of memory.

<!--more-->

The code I ended up with is listed below:

{% highlight nasm %}
; A little bit shorter version of the program can be created, when using a temporary variable
; instead of the X-Register.
.ORG $4000
main:
CLV
JSR bMult	; Perform multiplication A*B with the booth-method.
LDA R+1		; Load higher-Byte of result to Accumulator.
LDX R		; Load lower-Byte of result to X-Register
RTS		; Stop program.


bMult:	LDA A	; Load first operand.
BEQ bMultE	; stop if first operand is 0.
STA R		; store in lower byte of result. Will be shifted out of it later.
ASL		; Determine positions where additions or subtractions have to
EOR A		; be performed by using XOR. For every 1 in the X-Register a
TAX		; addition or subtraction has to be performed!
LDY #8		; Loop-Counter
bLoop: BVS bOvflw ; If B=$80 we get an overflow for the first subtraction, ignore sign!
LDA R+1		; Roll Result to the right. Remember that A is in the lower Byte,
ASL		; by shifting the next A-Bit into the carry flag we can determine
bOvflw:	ROR R+1	; later, what operation has to be performed (Addition or subtration);
ROR R		; The Carry-Flag first has to be saved to the stack, because it will
PHP		; be changed in the following lines. [*(1)]
TXA		; Shift X-Register to the right. By doing this we can check if any
LSR		; operation has to be performed (Addition/Subtraction). This is the
TAX		; case if the Carry-Flag is equal to 1.
PLA		; Restore Status-Register from *(1) to Accumulator.
BCC bLoopE	; Branch if no addition/subtraction has to be done...
LSR		; By shifting accumulator we get the old Carry-Flag from (*1).
LDA R+1		; Load result
BCC bAdd	; We can now decide if we have to add or subtract. Branch if we add.
SBC B		; Do a subtraction. We do not have to set the Carry-flag explicitly,
JMP bCont	; because we are sure the C-Flag is already set (based on the branch).
bAdd: ADC B	; Perform an addition. We do not have to reset the Carry-flag		
bCont: STA R+1	; Store result of addition/subtraction.
bLoopE: DEY	; Decrement loop-counter.
BPL bLoop       ; Do loop exactly 8 times.
bMultE: RTS	; leave this subroutine. The result is in the variable R.

.ORG $4500
A: .BYTE $AA	; First factor. 1 Byte.
B: .BYTE $81	; Second factor. 1 Byte.
R: .WORD $0000	; The result. Needs two bytes.
{% endhighlight %}

In one of the following posts I will describe the ideas behind the Booth method in more detail.
