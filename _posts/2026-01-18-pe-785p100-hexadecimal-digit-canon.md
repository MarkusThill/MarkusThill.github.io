---
layout: post
title: "The Hexadecimal Digit Canon Challenge"
modified:
categories: [programming, algorithms, combinatorics]
description: "A combinatorial programming challenge set in base 16: define a digit-canonical form for hexadecimal numbers and compute the cumulative sum of these canonical values across rapidly growing digit ranges. Simple to state, but requiring careful counting and optimization at scale."
tags: [combinatorics, number-theory, digit-dp, algorithms, optimization, hexadecimal, programming-puzzle]
thumbnail: assets/img/2026-01-17-hexadecimal-digit-canon.png
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-01-17T15:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
images:
  compare: false
  slider: false
---

In the Hexadecimal Canon, every number is first stripped of all insignificant zeros and reordered into its most "pure" form. The value of a number is not what it looks like at first glance, but what remains after this canonical purification.

All numbers in this problem are written in **base 16 (hexadecimal)**. The available digits are

$$
0,1,2,3,4,5,6,7,8,9,\text{A},\text{B},\text{C},\text{D},\text{E},\text{F},
$$

with $$\text{A}=10,\dots,\text{F}=15.$$

<br>

### The Digit–Canonical Function

For any **positive hexadecimal integer** $$d > 0$$, define the function $$f(d)$$ as follows:

1. Write $$d$$ in hexadecimal.
2. Sort its hexadecimal digits in **ascending order**.
3. Remove **all zero digits**.
4. Interpret the remaining digits again as a hexadecimal number.

Since $d > 0$, removing zero digits always leaves at least one hexadecimal digit.

<br>

### Examples

- **Example 1:**
  $$d = \texttt{0x3A04}$$. 
  Digits: $$3, A, 0, 4.$$ Sorted: $$0, 3, 4, A.$$  Remove zeros → $$3, 4, A$$.
  Result: $$f(\texttt{0x3A04}) = \texttt{0x34A}$$

- **Example 2**
  $$d = \texttt{0xF102}$$. Digits: $$F, 1, 0, 2$$. Sorted: $$0, 1, 2, F$$. Remove zeros → $$1, 2, F$$. Result: $$f(\texttt{0xF102}) = \texttt{0x12F}$$

- **Example 3**
  $$d = \texttt{0x800}$$. Digits: $$8, 0, 0$$. Sorted: $$0, 0, 8$$. Remove zeros → $$8$$. Result: $$f(\texttt{0x800}) = \texttt{0x8}$$

- **Example 4:**  $d = \texttt{0xA11B0}$. Digits: $A,1,1,B,0$. Sorted: $0,1,1,A,B$.  Remove zeros → $1,1,A,B$. Result: $f(\texttt{0xA11B0}) = \texttt{0x11AB}$.

<br>

### The Cumulative Sum

Let $$S(n)$$ denote the sum of $$f(d)$$ over **all positive hexadecimal integers with at most $$n$$ hexadecimal digits**.

For example:
- For $$n = \texttt{0x1}$$, the result is
  $$
  S(\texttt{0x1}) = \texttt{0x78}
  $$
- For $$n = \texttt{0x3}$$, the result is
  $$
  S(\texttt{0x3}) = \texttt{0x4077C0}
  $$

> **Important:** All values of $$S(n)$$ are to be reported **in hexadecimal notation**.

<br>
## Challenge Levels 🏅

Compute $$S(n)$$ for the following four difficulty tiers:

| Tier | Value of $$n$$ (hexadecimal) | Your Result (hexadecimal) |
|------|------------------------------|---------------------------|
| 🎗 Warm-up | $$n = \; \texttt{0x5}$$ | $$S(n) = \;\_\_\_\_\_\_\_\_\_\_\_\_$$ |
| 🥉 Bronze | $$n = \; \texttt{0xA}$$ | $$S(n) = \;\_\_\_\_\_\_\_\_\_\_\_\_$$ |
| 🥈 Silver | $$n = \; \texttt{0xAA}$$ | $$S(n) = \;\_\_\_\_\_\_\_\_\_\_\_\_\, \, $$ (first & last 10 hex digits) |
| 🥇 Gold | $$n = \; \texttt{0xAAA}$$ | $$S(n) \equiv \;\_\_\_\_\_\_\_\_\_\_\_\_  \pmod{\texttt{0x1FFFFFFFFFFFFFFF}} $$ |

<br> 

For the **silver** medal, report **only** the **first 10** and **last 10** hexadecimal digits of $$S(n)$$.  
Here, "first 10" means the first 10 digits of the standard hexadecimal representation of $$S(n)$$, and "last 10" means the last 10 digits (equivalently $$S(n) \bmod 16^{10}$$). The problem is designed so that **neither part has leading zeros**, and both substrings consist of exactly 10 hexadecimal digits.

For the **gold** medal, report your hexadecimal answer **modulo** $$\texttt{0x1FFFFFFFFFFFFFFF}.$$



<div class="answer-checker" style="border:1px solid #ddd;padding:1rem;border-radius:0.75rem;margin:1rem 0;">
  <p><strong>Check your solution</strong> (enter hex, e.g. <code>34A</code> or <code>34a</code>):</p>

  <label>🎗 Warm-up (n = 0x5):</label><br/>
  <input id="ans_warmup" type="text" style="width: 100%; max-width: 520px;" placeholder="your hex answer"/>
  <button onclick="checkAnswer('warmup')" style="margin-top:0.5rem;">Check</button>
  <div id="msg_warmup" style="margin-top:0.5rem;"></div>

  <hr style="margin:1rem 0;"/>

  <label>🥉 Bronze (n = 0xA):</label><br/>
  <input id="ans_bronze" type="text" style="width: 100%; max-width: 520px;" placeholder="your hex answer"/>
  <button onclick="checkAnswer('bronze')" style="margin-top:0.5rem;">Check</button>
  <div id="msg_bronze" style="margin-top:0.5rem;"></div>

  <hr style="margin:1rem 0;"/>


<label>🥈 Silver (n = 0xAA):</label><br/>

<div style="display:flex; align-items:center; justify-content:flex-start;">
  <!-- FIXED 520px inputs block (matches other inputs exactly) -->
  <div
    style="
      display:flex;
      gap:0.5rem;
      flex:0 0 520px;   /* <-- key: do NOT grow/shrink in the row */
      width:520px;      /* <-- hard match with other inputs */
      margin-right:0.5rem;
      box-sizing:border-box;
    "
  >
    <input
      id="ans_silver_prefix"
      type="text"
      style="flex:1 1 0; box-sizing:border-box;"
      placeholder="first 10 hex digits"
      maxlength="10"
    />
    <input
      id="ans_silver_suffix"
      type="text"
      style="flex:1 1 0; box-sizing:border-box;"
      placeholder="last 10 hex digits"
      maxlength="10"
    />
  </div>

  <button onclick="checkSilver()" style="white-space:nowrap;">
    Check
  </button>
</div>

<div id="msg_silver" style="margin-top:0.5rem;"></div>




  <hr style="margin:1rem 0;"/>

  <label>🥇 Gold (n = 0xAAA) mod 0x1FFFFFFFFFFFFFFF:</label><br/>
  <input id="ans_gold" type="text" style="width: 100%; max-width: 520px;" placeholder="your hex answer (mod ...)"/>
  <button onclick="checkAnswer('gold')" style="margin-top:0.5rem;">Check</button>
  <div id="msg_gold" style="margin-top:0.5rem;"></div>
</div>


<script>
  // ------------- configure expected hashes (hex of SHA-256 digest) -------------
  const EXPECTED_SHA256_HEX = {
    warmup: "f25b4ef775f23326522a5ab6cd75aa122828a056f22a2d801d195814112056b2",
    bronze: "60a8a313a5dd7919bb5d7883c5bf356ea68c65baedcffd274782a07d8cb098c3",
    silver: "0b1afa52c14209b2fb8fa80c6deb530666c0f5efc48b4e4e0ad98978225d17cc",
    gold:   "5052d8df7c751051a386c696777e90903067ab3906eeff8d85fc200a53edc2e6",
  };

  // Optional "pepper" (not a real secret in client-side JS, but stops copy/paste hashing mistakes)
  const PEPPER = "hex-digit-canon-v1";

  function normalizeHexInput(s) {
    // Normalize common formatting differences:
    // - trim
    // - remove "0x" prefix if present
    // - remove underscores/spaces
    // - uppercase
    const t = (s ?? "").trim().replace(/^0x/i, "").replace(/[\s_]+/g, "").toUpperCase();
    // Allow empty? Treat empty as invalid.
    return t;
  }

  async function sha256Hex(text) {
    const data = new TextEncoder().encode(text);
    const digest = await crypto.subtle.digest("SHA-256", data);
    const bytes = new Uint8Array(digest);
    return Array.from(bytes, b => b.toString(16).padStart(2, "0")).join("");
  }

  async function checkAnswer(tier) {
    const input = document.getElementById(`ans_${tier}`);
    const msg = document.getElementById(`msg_${tier}`);

    const norm = normalizeHexInput(input.value);
    if (!norm) {
      msg.innerHTML = "<span style='color:#b00;'>Please enter a hex value.</span>";
      return;
    }

    // Hash normalized answer + pepper (so you hash exactly what you intend)
    const got = await sha256Hex(`${PEPPER}|${tier}|${norm}`);

    if (got === EXPECTED_SHA256_HEX[tier]) {
      msg.innerHTML = "<span style='color:#0a0;'><strong>Correct ✅</strong></span>";
    } else {
      msg.innerHTML = "<span style='color:#b00;'><strong>Not correct ❌</strong></span>";
    }
  }
</script>

<script>
async function checkSilver() {
  const prefixInput = document.getElementById("ans_silver_prefix");
  const suffixInput = document.getElementById("ans_silver_suffix");
  const msg = document.getElementById("msg_silver");

  const prefix = normalizeHexInput(prefixInput.value);
  const suffix = normalizeHexInput(suffixInput.value);

  if (prefix.length !== 10 || suffix.length !== 10) {
    msg.innerHTML =
      "<span style='color:#b00;'>Please enter exactly 10 hex digits for both prefix and suffix.</span>";
    return;
  }

  // Canonical message for hashing
  const payload = `${PEPPER}|silver|${prefix}|${suffix}`;
  const got = await sha256Hex(payload);

  if (got === EXPECTED_SHA256_HEX.silver) {
    msg.innerHTML = "<span style='color:#0a0;'><strong>Correct ✅</strong></span>";
  } else {
    msg.innerHTML = "<span style='color:#b00;'><strong>Not correct ❌</strong></span>";
  }
}
</script>

💡 Solution coming soon: A full, step-by-step solution—including the underlying combinatorics and an efficient implementation—will be published on this blog shortly. Stay tuned!