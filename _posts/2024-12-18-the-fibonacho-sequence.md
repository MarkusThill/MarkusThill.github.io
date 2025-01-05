---
layout: post
title: "Challenge: The Sequence of Fibonacho"
modified:
categories: 
tags: [fibonacci, number theory, math, python, programming]
description: "The Fibonacho Sequence is a playful and intriguing twist on the classical Fibonacci numbers. Unlike its better-known cousin, the Fibonacho Sequence does not follow the same simple recurrence relation. Instead, it introduces a slightly different structure, making it a entertaining puzzle for math enthusiasts and programmers alike. Are you ready to dive into the challenge?"
thumbnail: assets/img/fibonacho-thumbnail.webp
giscus_comments: true
featured: False
share:
toc:
  beginning: true
date: 2025-01-05 12:16:00
pretty_table: true
related_posts: true
---

{% include figure.liquid 
   path="assets/img/fibonacho-16-9.webp" 
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="90%"  
   caption="How OpenAI's OpenAI's DALL·E model imagines the Fibonacho Sequence."  
%}

The Fibonacho Sequence is a intriguing twist on the classical Fibonacci numbers. Unlike its better-known cousin, the Fibonacho Sequence does not follow the same simple recurrence relation. Instead, it introduces a slightly different structure, making it an entertaining little puzzle for math enthusiasts and programmers alike.

In this challenge, you will explore the sequence's definition, uncover its recurrence relation, and tackle a series of progressively more complex questions. Starting with small values and scaling up to massive indices, the goal is to unlock the underlying properties of this unique sequence, culminating in the analysis of numbers with hundreds of digits.

Are you ready to dive into the challenge and see how far your skills can take you? Let’s get started!

## Sequence Definition and Initial Values

The Fibonacho Sequence starts with a few predefined values and grows according to a hidden pattern. Unlike the Fibonacci sequence, which has a simple and elegant formula, the Fibonacho Sequence is less straightforward.
Below is a table of the first few elements, $$F_n$$ , of the **Fibonacho Sequence**:

|   n       | 0    | 1       | 2    | 3     | 4     | 5     | 6     | 7     | 8     | 9     | 10    | 11    | 12    | 13    | 14    | 15    | 16    | 17    | 18    | 19    | 20                    |
|----------|------|------|------|------|------|------|------|------|------|------|------|------|------|------|------|------|------|------|------|------|-------|
|F<sub>n</sub>| 0    | 0    | 0    | 1    | 1    | 1    | 2    | 4    | 6    | 9   | 15   | 25   | 40   | 64   | 104   | 169   | 273   | 441   | 714   | 115 |1870                       |

<p></p>
Furthermore, you are given $$F_{100} = 97905340104793732225$$. Notice how the sequence grows, but not in the same way as the Fibonacci numbers.

## Part 1: Understanding the Problem & Deriving the Recurrence Relation

The challenge begins with uncovering the recurrence relation that governs the Fibonacho Sequence. A recurrence relation is a formula that expresses each term of a sequence as a function of its preceding terms. However, unlike the Fibonacci sequence’s simple $$F_n = F_{n-1} + F_{n-2}$$, the Fibonacho Sequence defies such simplicity.
Your task is to deduce the recurrence relation by analyzing the given terms. 

Which general recurrence relation describes the sequence above?

**Note again:** It is *NOT* the recurrence relation for the *Fibonacci numbers*, since, for example, $$F_{17} \ne F_{15} + F_{16}$$.

## Part 2: Predicting Digits at Larger Indices

Now that you’ve explored the recurrence relation, it’s time to tackle larger terms in the sequence. You are given that:
- The **first 10 digits** of $$F_{1000}$$ are $$1201386106$$
- The **last 10 digits** of $$F_{1000}$$ are $$1044856625$$

What are the **first** and **last** $$10$$ digits of $$F_{10000}$$?

## Part 3: Scaling Up!

In this part, the challenge becomes even more daunting. You are now tasked with examining the **first** and **last** $$\mathbf{100}$$ digits of massive terms like $$F_{7^7} = F_{823543}$$. 

For reference, you are given the first and last digits of  $$F_{7^{7}} = F_{823543}$$:

| $$F_{7^{7}}$$ | digits |
|----------|----------|
| first 100   |  2513371832737186384322330481943752132726740483311444508185490845781280728438771549838156508593799526  |
| last 100   | 739646476432651186655886864569054345315965466581269946302070897583058681065487248400966951495110916   |


<!---
Also, you are given the first and last digits of  $$F_{3^{3^3}} = F_{7625597484987}$$:
| $$F_{3^{3^3}}$$ | digits |
|-------------|----------|
| first 100   | 4986623353623225796889809195057463248297307920121244456898480218186054716988773908418646784061935629   |
| last 100   | 5456086982991487918462492187737814960938573182838430189682893449207863706511044683868046511372105169   |
--->


<p></p>
What are the **first** and **last** $$100$$ digits of $$F_{4^{4^4}}$$, $$F_{5^{5^5}}$$, and $$F_{6^{6^6}}$$ ?

---

Stay tuned, as I will reveal the solution and dive deeper into a few properties of the Fibonacho Sequence in a future blog post!
