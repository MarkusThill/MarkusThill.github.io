---
layout: post
title: "Don't Drink and Derive&#58; A Simple Proof that 1 = 2"
modified:
categories: 
tags: [math]
description: "In this blog post, we present a fun little proof that 1 is actually equal to 2. Or is it?"
thumbnail:
giscus_comments: true
featured: False
share:
date: 2024-12-12 13:16:00
---

Let
$$
\begin{align}
	a,b,c \in \mathbb{R}	 \backslash \{ 0\}.
\end{align}
$$

Now let us define a simple equation
$$
\begin{align}
	a=b+c
\label{eq:start}
\end{align}
$$

and play around with it a little bit.

<!--more-->

$$
\begin{align*}
	a   &= b+c 		&  & \vert\ \cdot a\\
	a^2 &= ab + ac	&  & \vert\ -b^2, -c^2\\
	a^2-b^2-c^2 &= ab + ac - b^2 -c^2 &  & \vert\ -2bc\\
	a^2-b^2-c^2 -2bc &= ab + ac - b^2 -c^2 -2bc &  & \\
	a^2-b^2-c^2 -2bc &= ab - b^2 - bc + ac - bc - c^2 &  & \\
	a^2-b^2-c^2 -2bc &= b(a - b - c) + c(a - b - c) &  & \\
\end{align*}
$$

We then add the terms $$ab$$ and $$ac$$ to the left side of the equation and then subtract them again and rearrange the terms of the equation:

$$
\begin{align*}
	a^2-b^2-c^2 -2bc + ab -ab +ac -ac &= b(a - b - c) + c(a - b - c) &  & \\
	a^2 + ab +ac -ab -b^2 -bc -ac -bc -c^2  &= b(a - b - c) + c(a - b - c) &  & \\
	(a^2 + ab +ac) - (ab +b^2 +bc) - (ac +bc +c^2)  &= b(a - b - c) + c(a - b - c) &  & \\
	a(a + b +c) - b(a +b + c) - c(a +b +c)  &= b(a - b - c) + c(a - b - c) &  & \\
	(a + b +c) (a-b-c)  &= b(a - b - c) + c(a - b - c) &  & \vert\ \div (a-b-c)\\
\end{align*}
$$

Now, the equation simplifies to:

$$
\begin{align*}
	a+b+c &= b+c \\
	a+ (b+c) &= (b+c) \\
\end{align*}
$$

If we use our original relation $$a=b+c$$ from Eq. \eqref{eq:start} and insert $$a$$ for the term $$b+c$$ we finally get:

$$
\begin{align*}
	a+ a &= a &  &  \\
	2a &= a &  & \vert\ \div a \\
	2 &= 1
\end{align*}
$$

So, starting with Eq. \eqref{eq:start} we could prove that actually $$1=2$$. Or is there something wrong up there?
