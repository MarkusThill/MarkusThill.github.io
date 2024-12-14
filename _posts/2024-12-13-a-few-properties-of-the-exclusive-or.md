---
layout: post
title: "Some Interesting Properties of the Exclusive Or (XOR)"
modified:
categories: 
tags: [xor, boolean algebra, digital systems]
description: "The exclusive-OR — also known as exclusive disjunction (short: XOR) or antivalence — is a Boolean operation that outputs true only when exactly one of its two inputs is true (i.e., when the inputs differ). XOR has numerous applications, including cryptography, Gray codes, parity checks, and CRC checks, among others. In this blog post, we will explore some of its interesting properties that can be useful in practice."
thumbnail: assets/img/xor.webp
giscus_comments: true
featured: False
share:
date: 2024-12-13 08:16:00
---

The exclusive-OR -- sometimes also exclusive disjunction (short: XOR) or antivalence -- is a boolean operation which only outputs true if only exactly one of its both inputs is true (so if both inputs differ). There are many applications where the XOR is used, for instance in cryptography, gray codes, parity and CRC checks and certainly many more. Commonly, the $$\oplus$$ symbol is used to denote the XOR operation. Here, we will use the $$\nleftrightarrow$$ symbol for the Exclusive-OR and $$\leftrightarrow$$ for its negation, the biconditional operator.
In this blog post we will look at a few of its interesting properties which can be useful.

Let us start with the truth table of the Exclusive-OR ($$\nleftrightarrow$$) and the biconditional:

| a | b | a $$\nleftrightarrow$$ b | a $$\leftrightarrow$$ b |
| ---: |:---:|:---:|:---|
| 0 | 0 | 0 | 1 |
| 0 | 1 | 1 | 0 |
| 1 | 0 | 1 | 0 |
| 1 | 1 | 0 | 1 |

<!--more-->

### Definition

From this table we can extract the following equations, which is the most commonly used definition of the XOR operation:

$$
\begin{align}
a \nleftrightarrow b = \bar a b \vee a \bar b  \quad \mbox{and} \quad  a \leftrightarrow b = \bar a \bar b \vee a b
\label{eq:definition}
\end{align}
$$

### Inverse Element

Note that the logical AND operation ($$a \wedge b$$) is written as $$ab$$. Both operations have an inverse element (1 and 0) so that

$$
\begin{align}
a \nleftrightarrow 1 = \bar a \quad \mbox{and} \quad a \leftrightarrow 0 = \bar a \\
a \nleftrightarrow \bar a = 1 \quad \mbox{and} \quad a \leftrightarrow \bar a = 0
\end{align}
$$

### Neutral Element

For the Exclusive-OR and the biconditional also a neutral element exists (0 and 1):

$$
\begin{align}
a \nleftrightarrow 0 = a \quad \mbox{and} \quad a \leftrightarrow 1 = a \\
\end{align}
$$

### Idempotency
It can easily be shown that the the XOR does not fulfil the idempotency property, which states that for any operation $$\circ$$ we have $$a \circ a = a$$. From the truth table we can see that

$$
\begin{align}
a \nleftrightarrow a = 0 \quad \mbox{and} \quad a \leftrightarrow a = 1. \\
\end{align}
$$.


### Inverse of the Exclusive OR
We have already mentioned that the inverse of the XOR is the biconditional operator. This can also be easily seen from the truth table. However, it is also possible to show this formally:

$$
\begin{align}
a \nleftrightarrow b = \overline{a \leftrightarrow b} \quad \mbox{and} \quad  a \leftrightarrow b = \overline{a \nleftrightarrow b} \label{eq:inverseXOR}
\end{align}
$$

since -- using Eq. \eqref{eq:definition} :

$$
\begin{align*}
& a \nleftrightarrow b =  \bar a b \vee a \bar b = \overline{ \overline{\bar a b} \wedge \overline{a \bar b}} = \overline{(a \vee \bar b) \wedge (\bar a \vee b)} \\
&= \overline{a(\bar a \vee b) \vee \bar b (\bar a \vee b)} = \overline{ab \vee \bar a \bar b}\\
&= \overline{a \leftrightarrow b}
\end{align*}
$$


### Commutativity

Commutativity is given in both cases as well:

$$
\begin{align}
a \nleftrightarrow b = b \nleftrightarrow a \quad \mbox{and} \quad a \leftrightarrow b = b \leftrightarrow a
\label{eq:Commutativity}
\end{align}
$$

since

$$
\begin{align}
a \nleftrightarrow b = \bar a b \vee a \bar b =  \bar b a \vee b \bar a  = b \nleftrightarrow a \quad (\mbox{analogously for} \leftrightarrow )\\
\end{align}
$$

### Associativity

Also the associative property is fulfilled:

$$
\begin{align}
a \nleftrightarrow b \nleftrightarrow  c = (a \nleftrightarrow b) \nleftrightarrow  c = a \nleftrightarrow (b \nleftrightarrow  c) \\
a \leftrightarrow b \leftrightarrow  c = (a \leftrightarrow b) \leftrightarrow  c = a \leftrightarrow (b \leftrightarrow  c) \\
\end{align}
$$

since -- using rules \eqref{eq:definition} and \eqref{eq:inverseXOR}.

$$
\begin{align*}
& a \nleftrightarrow (b \nleftrightarrow  c) = a \nleftrightarrow (\bar b c \vee b \bar c) = \bar a (\bar b c \vee b \bar c) \vee a \overline{\bar b c \vee b \bar c}  \\
&= \bar a \bar b c \vee \bar a b \bar c \vee a( b \vee \bar c) (\bar b \vee c) = \bar a \bar b c \vee \bar a b \bar c \vee abc \vee a \bar b \bar c \\
&= (ab \vee \bar a \bar b)c \vee (\bar a b \vee a \bar b)\bar c = \overline{a \nleftrightarrow b} c \vee (a \nleftrightarrow b) \bar c  \\
&= (a \nleftrightarrow b) \nleftrightarrow  c = a \nleftrightarrow b \nleftrightarrow  c
\end{align*}
$$


### Distributivity

As we will see later, the conjunction (AND) and Exclusive-OR (biconditional) represent the multiplication and addition operations of a Galois field GF(2), and in such a field they follow the distributive law:

$$
\begin{align}
a(b \nleftrightarrow c) = ab \nleftrightarrow ac \quad \mbox{and} \quad a(b \leftrightarrow c) = ab \leftrightarrow ac
\end{align}
$$

since -- with Eq. \eqref{eq:inverseXOR}:

$$
\begin{align*}
a(b \nleftrightarrow c) &\overset{!}{=} ab \nleftrightarrow ac \\
a( b \bar c \vee \bar b c) &\overset{!}{=} ab \overline{ac} \vee \overline{ab} bc \\
a b \bar c \vee a \bar b c &\overset{!}{=} ab (\bar a \vee \bar c) \vee (\bar a \vee \bar b) ac \\
a b \bar c \vee a \bar b c &= ab \bar c \vee a \bar b c
\end{align*}
$$

This holds accordingly for the biconditional operator.

### Inverting a single Operand

$$
\begin{align}
\bar a \nleftrightarrow b = \overline{a \nleftrightarrow b}   \quad \mbox{and} \quad  \bar a \leftrightarrow b = \overline{a \leftrightarrow b}
\label{eq:invOne}
\end{align}
$$

since -- with Eq. \eqref{eq:inverseXOR}:

$$
\begin{align*}
\bar a \nleftrightarrow b = ab \vee \bar a \bar b = a \leftrightarrow b   = \overline{a \nleftrightarrow b}.
\end{align*}
$$

### Inverting both Operands

$$
\begin{align}
\bar a \nleftrightarrow \bar b = a \nleftrightarrow b   \quad \mbox{and} \quad  \bar a \leftrightarrow \bar b = a \leftrightarrow b
\label{eq:invBoth}
\end{align}
$$

which can be shown trivially with \eqref{eq:definition}:

$$
\begin{align*}
\bar a \nleftrightarrow \bar b = a \bar b \vee \bar a b = a \nleftrightarrow b \\
\end{align*}
$$

### Expressing the Logical OR in Terms of the Exclusive-OR
We can find the following expression:

$$
\begin{align}
a \vee b = (a \nleftrightarrow b) \vee ab
\label{eq:OR-XOR}
\end{align}
$$

since -- by expanding a and b, with $$ (ab \vee a\bar b) = a(b \vee \bar b) = a $$:

$$
\begin{align*}
a\vee b &= (ab \vee a\bar b) \vee (ab \vee \bar a b) = \bar a b \vee a \bar b \vee ab \\
&= (a \nleftrightarrow b) \vee ab
\end{align*}
$$

Since the above equation again contains a disjunction (OR), this does not appear like any improvement, however, this rule can be helpful in deriving many other relations.
For example, let us apply the rule \eqref{eq:OR-XOR} to itself:

Let us first identify:

$$
\begin{align*}
A &= a \nleftrightarrow b \\
B &= ab
\end{align*}
$$

Then we have (inserting the original expressions for $$A$$ and $$B$$ after some time again):

$$
\begin{align*}
A \vee B &= (A \nleftrightarrow B) \vee AB \\
&= (A \nleftrightarrow B) \vee (a \nleftrightarrow b)ab \\
&= (A \nleftrightarrow B) \vee (\bar a b \vee a \bar b)ab \\
\end{align*}
$$

Since the terms $$\bar a b$$ and $$a \bar b$$ are disjunct to $$ab$$, the above expression simplifys to:

$$
\begin{align*}
(A \nleftrightarrow B) \vee (\bar a b \vee a \bar b)ab &= A \nleftrightarrow B \\
\end{align*}
$$

This leads finally to some interesting relation:

$$
\begin{align}
a \vee b &= (a \nleftrightarrow b) \vee ab \nonumber\\
&= A \nleftrightarrow B \\
&= a \nleftrightarrow b \nleftrightarrow ab \nonumber
\end{align}
$$

### Expressing the Logical AND in Terms of the Exclusive-OR
Analogously to the previous paragraph, one can derive some interesting relations for the logical AND (conjunction):

$$
\begin{align}
a \wedge b = (a \leftrightarrow b) \wedge (a \vee b)
\end{align}
$$

and

$$
\begin{align}
a \wedge b = a \leftrightarrow b \leftrightarrow (a \vee b)
\end{align}
$$


### The Logical OR of pairwise disjunct Terms

Using the rule \eqref{eq:OR-XOR} we can find another interesting relation for disjunctive forms where all terms are pairwise disjunct. Consider the following easy example  -- applying rule \eqref{eq:OR-XOR}:

$$
\begin{align}
\bar a b\vee a \bar b &= (\bar a b \nleftrightarrow a \bar b) \vee (\bar a b\wedge a \bar b) \nonumber \\
&= \bar a b \nleftrightarrow a \bar b
\label{eq:xorAbsurdum}
\end{align}
$$

As a side note, we can also write above relation backwards, so that:

$$
\begin{align}
\bar a b \nleftrightarrow a \bar b &= \bar a b\vee a \bar b \nonumber \\
&= a \nleftrightarrow b
\end{align}
$$

With Eq.\eqref{eq:xorAbsurdum} we have an important relation that states that all OR operations in an disjunctive form can be simply replaced with an XOR, if all terms are pairwise disjunct. For example, the rule can be applied to the following disjunctive form:

$$
\begin{align*}
abc \vee \bar a bc \vee ab \bar c \\
= abc \nleftrightarrow \bar a bc \nleftrightarrow ab \bar c.
\end{align*}
$$

### The Logical Biconditional and Exclusive-OR revisited

Sometimes it is possible to replace all biconditional operations in an equation by Exclusive-ORs. Consider the following example -- with Eq. \eqref{eq:inverseXOR} and Eq. \eqref{eq:invOne}:

$$
\begin{align*}
a \leftrightarrow b \leftrightarrow c &= \overline{a \nleftrightarrow b} \leftrightarrow c \\
&= \overline{(a \nleftrightarrow b) \leftrightarrow c} \\
&= a \nleftrightarrow b \nleftrightarrow c.
\end{align*}
$$

Or, in short:

$$
\begin{align}
a \leftrightarrow b \leftrightarrow c &= a \nleftrightarrow b \nleftrightarrow c.
\label{eq:BicondEqXOR}
\end{align}
$$

### The combined Associative Property of the Logical Biconditional and the Exclusive-OR

Similarly to before, where we showed the associative property of the biconditional and the exclusive-OR for both cases separately, we can also show that the associative property also holds for mixed terms -- with Eq.\eqref{eq:inverseXOR}, \eqref{eq:invOne} and \eqref{eq:BicondEqXOR}:

$$
\begin{align*}
(a \nleftrightarrow b) \leftrightarrow c &\overset{!}{=} a \nleftrightarrow (b \leftrightarrow c) \\
\overline{a \leftrightarrow b} \leftrightarrow c &\overset{!}{=} a \nleftrightarrow \overline{b \nleftrightarrow c} \\
\overline{a \leftrightarrow b \leftrightarrow c} &\overset{!}{=} \overline{a \nleftrightarrow b \nleftrightarrow c} \\
a \leftrightarrow b \leftrightarrow c &= a \nleftrightarrow b \nleftrightarrow c \\
\end{align*}
$$

This allows us to state:
$$
\begin{align}
(a \nleftrightarrow b) \leftrightarrow c = a \nleftrightarrow (b \leftrightarrow c) = a \nleftrightarrow b \leftrightarrow c
\label{eq:mixedassociative}
\end{align}
$$

### The combined Commutative Property of the Logical Biconditional and the Exclusive-OR
After we showed the combined associative property of the logical biconditional and the exclusive-OR, we accordingly show commutativity. We only need Eq. \eqref{eq:Commutativity} and \eqref{eq:mixedassociative}. The argumentation is then rather trivial:

$$
\begin{align*}
&a \nleftrightarrow b \leftrightarrow c = (a \nleftrightarrow b) \leftrightarrow c = (b \nleftrightarrow a) \leftrightarrow c \\
= &b \nleftrightarrow a \leftrightarrow c = b \nleftrightarrow (a \leftrightarrow c) = b \nleftrightarrow (c \leftrightarrow a) \\
= &b \nleftrightarrow c \leftrightarrow a = (b \nleftrightarrow c) \leftrightarrow a = (c \nleftrightarrow b) \leftrightarrow a \\
= & c \nleftrightarrow b \leftrightarrow a = \cdots \\
= &a \nleftrightarrow b \leftrightarrow c = (a \nleftrightarrow b) \leftrightarrow c =
 c \leftrightarrow (a \nleftrightarrow b) \\
= & c \leftrightarrow a \nleftrightarrow b = (c \leftrightarrow a) \nleftrightarrow b =
  b \nleftrightarrow (c \leftrightarrow a) \\
= & b \nleftrightarrow c \leftrightarrow a = (b \nleftrightarrow c) \leftrightarrow a =
   a \leftrightarrow (b \nleftrightarrow c) \\
= & a \leftrightarrow b \nleftrightarrow c = \cdots
\end{align*}
$$

In summary, we can write:

$$
\begin{align}
a \nleftrightarrow b \leftrightarrow c
= b \nleftrightarrow a \leftrightarrow c
= b \nleftrightarrow c \leftrightarrow a
= c \nleftrightarrow b \leftrightarrow a = \cdots \nonumber \\
= c \leftrightarrow a \nleftrightarrow b
= b \nleftrightarrow c \leftrightarrow a
= a \leftrightarrow b \nleftrightarrow c = \cdots
\label{eq:combinedCommutative}
\end{align}
$$

Hence, all terms in an mixed expression of XORs and biconditionals are pairwise interchangeable. This is a very important observation which can often help in practice.

### Replacing Exclusive-Or Operations in an Expression with Biconditionals
Assume, we have an expression in the form

$$
\begin{align*}
f(x_1, x_2, \ldots, x_n) = x_1 \nleftrightarrow x_2 \nleftrightarrow \ldots \nleftrightarrow x_n.
\end{align*}
$$

We want to replace all $$\nleftrightarrow$$ operations with $$\leftrightarrow$$. How can we achieve this? Actually, it is not that difficult. We can recursively apply the rules \eqref{eq:inverseXOR}, \eqref{eq:invOne} and \eqref{eq:mixedassociative} in the following way:

$$
\begin{align*}
f(x_1, x_2, \ldots, x_n) &=
\overline{x_1 \leftrightarrow (x_2 \nleftrightarrow x_3 \nleftrightarrow \ldots \nleftrightarrow x_n)} \\
&= \overline{x_1 \leftrightarrow x_2 \nleftrightarrow x_3 \nleftrightarrow \ldots \nleftrightarrow x_n} \\
&= \overline{x_1 \leftrightarrow \overline{x_2 \leftrightarrow (x_3 \nleftrightarrow \ldots \nleftrightarrow x_n)}} \\
&= \overline{x_1 \leftrightarrow \overline{x_2 \leftrightarrow x_3 \nleftrightarrow \ldots \nleftrightarrow x_n}} \\
&= \overline{ \overline{x_1 \leftrightarrow x_2 \leftrightarrow x_3 \nleftrightarrow \ldots \nleftrightarrow x_n}} \\
&= x_1 \leftrightarrow x_2 \leftrightarrow x_3 \nleftrightarrow \ldots \nleftrightarrow x_n \\
&= x_1 \leftrightarrow x_2 \leftrightarrow x_3 \leftrightarrow \overline{\ldots \nleftrightarrow x_n} \\
&= \cdots
\end{align*}
$$

You can see where this is going: After replacing the first XOR we had a negation in the expression which vanished again after replacing the second XOR and then came back with the replacement of the third XOR. So, depending on the number of variables $$n$$, we either have a negation left in the end or not. This can be expressed with:

$$
\begin{align}
f(x_1, x_2, \ldots, x_n) &= x_1 \nleftrightarrow x_2 \nleftrightarrow \ldots \nleftrightarrow x_n \label{eq:replaceXOR} \\ \nonumber
&=
\begin{cases}
    x_1 \leftrightarrow x_2 \leftrightarrow \ldots \leftrightarrow x_n,& \text{if n is odd} \\  \nonumber
     \\
    \overline{x_1 \leftrightarrow x_2 \leftrightarrow \ldots \leftrightarrow x_n},& \text{if n is even}
\end{cases}\\
\end{align}
$$

Similarly, we find the following relation when we replace the biconditionals in an expression with the XOR operation:

$$
\begin{align}
f(x_1, x_2, \ldots, x_n) &= x_1 \leftrightarrow x_2 \leftrightarrow \ldots \leftrightarrow x_n \label{eq:replaceBiconditional} \\ \nonumber
&=
\begin{cases}
    x_1 \nleftrightarrow x_2 \nleftrightarrow \ldots \nleftrightarrow x_n,& \text{if n is odd} \\  \nonumber
     \\
    \overline{x_1 \nleftrightarrow x_2 \nleftrightarrow \ldots \nleftrightarrow x_n},& \text{if n is even}
\end{cases}\\
\end{align}
$$


### Mixed Representations of Biconditionals and Exclusive-ORs
Sometimes, one has mixed representations of biconditionals and exclusive-ORs, which cannot be implemented that efficiently in a digital circuit. In these cases it is possible to find representations consisting solely of XORs or solely of biconditionals. First, we have to bring our original representation in a form:

$$
f_\nleftrightarrow(x_1,x_2,\ldots,x_m) \circ f_\leftrightarrow(x_{m+1}, x_{m+1}, \ldots, x_n)
$$

where $$f_\nleftrightarrow$$ just consists of XOR operations and $$f_\leftrightarrow$$ just consists of biconditionals. For the $$\circ$$ symbol, either $$\nleftrightarrow$$ is inserted in case we want the final relation to consist of XORs, otherwise $$\leftrightarrow$$ is inserted. Note that the above representation with $$f_\nleftrightarrow$$ and $$f_\leftrightarrow$$ can be easily achieved by simply applying the commutative property from Eq. \eqref{eq:combinedCommutative} to your original relation. Then you are almost done: You just have to apply \eqref{eq:replaceXOR} to $$f_\nleftrightarrow(x_1,x_2,\ldots,x_m)$$  or \eqref{eq:replaceBiconditional} to $$f_\leftrightarrow(x_1,x_2,\ldots,x_m)$$ -- depending which operator you prefer -- and finally you have a nice representation containing either just XORs or just biconditionals.

#### Example
$$
\begin{align*}
f(x_1,x_2,x_3,x_4) &= x_1 \leftrightarrow x_2 \nleftrightarrow x_3 \leftrightarrow x_4 \\
&= x_1 \leftrightarrow x_2 \leftrightarrow x_3 \nleftrightarrow x_4 \\
&= f_\leftrightarrow(x_1,x_2,x_3) \nleftrightarrow x_4 \\
\end{align*}
$$

We replace the biconditionals in $$f_\leftrightarrow$$ with XORs:

$$
\begin{align*}
f_\leftrightarrow(x_1,x_2,x_3) &= x_1 \leftrightarrow x_2 \leftrightarrow x_3 \\
&= x_1 \nleftrightarrow x_2 \nleftrightarrow x_3
\end{align*}
$$

and insert back into the original equation:

$$
\begin{align*}
f(x_1,x_2,x_3,x_4) &= f_\leftrightarrow(x_1,x_2,x_3) \nleftrightarrow x_4 \\
&= x_1 \nleftrightarrow x_2 \nleftrightarrow x_3 \nleftrightarrow x_4
\end{align*}
$$
