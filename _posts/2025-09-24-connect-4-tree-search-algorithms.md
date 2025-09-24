---
layout: post
title: "Building Intelligent Agents for Connect-4&#58; Tree Search Algorithms"
modified: 2025-09-24T09:00:51+01:00
categories: [Programming]
description: "Learn how the Alpha-Beta search algorithm optimizes Minimax for Connect-4 by pruning unnecessary branches, improving efficiency, and enabling stronger gameplay strategies."
tags: [Connect-4, AI, tree-search, alpha-beta, minimax, transposition tables, opening databases, move ordering, bitboards]
thumbnail: assets/img/project_bitbully/c4-3.png
giscus_comments: true
toc:
  beginning: true
share: true
date: 2025-09-24T09:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
# related_publications: true
---

This post is the 2nd part of a series of 7 articles:

1. [Building Intelligent Agents for Connect-4&#58; First Steps]({% post_url  2025-07-05-connect-4-introduction-and-tree-search-algorithms %})
2. **[Building Intelligent Agents for Connect-4&#58; Tree Search Algorithms]({% post_url 2025-09-24-connect-4-tree-search-algorithms %})**
3. [Building Intelligent Agents for Connect-4&#58; Board Representations](#)
4. [Building Intelligent Agents for Connect-4&#58; Move Ordering](#)
5. [Building Intelligent Agents for Connect-4&#58; Transposition Tables](#)
6. [Building Intelligent Agents for Connect-4&#58; Opening Databases](#)
7. [Building Intelligent Agents for Connect-4&#58; Final Considerations](#)

To play Connect-4 perfectly, an agent must be capable of fully exploring the entire game tree—which, in the most extreme case, can span all 42 moves of the game. However, the search effort grows exponentially with depth, making this a significant computational challenge and requiring considerable development effort to achieve optimal play.  

This post (and the ones that follow) will introduce some of the techniques and strategies that make such an agent possible. In this article, we’ll focus on one of the fundamental methods for efficient game tree exploration: **alpha-beta search**.


## The Alpha-Beta Search

The **Alpha-Beta search** is an optimized version of the classic Minimax algorithm. While a simple Minimax search evaluates *every* node in the game tree, Alpha-Beta introduces two bounds—**alpha** and **beta**—to prune (cut off) large parts of the tree that cannot influence the final decision. The effectiveness of this pruning depends on factors such as the quality of the move ordering.  

The core idea is straightforward: because each player alternates between maximizing and minimizing outcomes, certain branches can be skipped if a better alternative is already known. Two key variables guide this process:  
- **Alpha** – the best score the *maximizing* player can guarantee so far (a lower bound).  
- **Beta** – the best score the *minimizing* player can guarantee so far (an upper bound).  

As the search progresses recursively through the tree, alpha and beta are updated and compared at each node. When the algorithm detects that further exploration cannot improve the current result, it prunes that branch. This pruning can occur at any level, not just near the root.  

From the maximizing player’s perspective, the procedure for processing a node is as follows:  
1. Generate all legal moves for the current state.  
2. Evaluate these moves in sequence.  
3. If any move returns a value **greater than or equal to beta**, the search stops at that node and returns beta (a **fail-high**). This indicates that the minimizing opponent will never allow this position to occur.  
4. If none of the moves improves alpha, the node returns alpha as a bound (**fail-low**), signaling that this position is not good enough to pursue.  
5. Only values between alpha and beta are considered **exact** evaluations; values outside this range are treated as bounds.  

As chess programmer [Bruce Moreland](http://web.archive.org/web/20040512194831/brucemo.com/compchess/programming/glossary.htm) explains succinctly:  

> *"A fail-high indicates that the search found something that was 'too good.' The opponent can avoid this position, so there’s no need to explore further. A fail-low indicates that the position was not good enough—we have a better alternative, and will not choose the move that leads here."*  

You can find a simplified pseudo-code implementation below, and the full implementation is available as `AlphaBetaAgent` in the appendix. Some of these elements will be discussed in greater depth in upcoming posts.


{% highlight C %}
double max(double alpha, double beta) {
  if(hasWin(playerMax))
    return +1;
  if(isDraw())
    return 0;
  if(bookEntryAvailable()) return bookValue(); // Opening Book
  if(hasTransTableEntry(board, mirroredBoard))
    return transTableEntryValue(board, mirroredBoard)
  generateMoves(max);
  sortMoves(max);
  if(isSymmetricPosition())
    removeSymMoves();
  while(hasMovesLeft(max)) {
    makeMove(max);
    value = min(alpha, beta);
    takeMoveBack(max);
    if(value >= beta) {
      putEntryInTranspositionTable();
      return beta;
    }
    if(value > alpha)
      alpha = value;
  }
  putEntryInTranspositionTable();
  return alpha;
}

double min(double alpha, double beta) {
  if(hasWin(min)) return -1;
  if(enhancedTranspositionCutoff(board, mirroredBoard))
    return ETCValue;
  generateMoves(min);
  sortMoves(min);
  if(isSymmetricPosition())
    removeSymMoves();
  while(hasMovesLeft(min)) {
    makeMove(min);
    value = max(alpha, beta);
    takeMoveBack(min);
    if(value <= alpha)
      return alpha;
    if(value < beta)
      beta = value;
  }
    return beta;
}

{% endhighlight %}


### The Negamax Variant

In our implementation, we use the **Negamax** variant of the Minimax algorithm. Negamax is mathematically equivalent to Minimax but simplifies the code by taking advantage of the symmetry between maximizing and minimizing players. Instead of maintaining two separate evaluation branches—one for the maximizing player and one for the minimizing player—Negamax represents both using a single recursive function. The idea is based on the relation:


$$    \min(a, b) = -\max(-a, -b) $$

At each step, the algorithm evaluates a move by calling itself recursively with inverted scores and a flipped sign, effectively switching the roles of the players. This reduces code complexity and makes implementing features like alpha-beta pruning more straightforward.

Negamax is widely used in game AI development for games like chess, checkers, and Connect-4 because it keeps the logic compact while maintaining the same performance and search results as the standard Minimax algorithm.

The corresponding code for our negamax implementation can be found on [GitHub](https://github.com/MarkusThill/BitBully/blob/9c8993b185662d800568494dd4983a7aa2bb7fb8/src/BitBully.h#L100).


<br>
## Additional Resources and Source Code

More recently, I developed a high-performance C++ and Python version of a Connect-4 solver called **BitBully**, available on [GitHub](https://github.com/MarkusThill/BitBully) and [PyPI](https://pypi.org/project/bitbully/). Also, check out the related [project page]({{ 'projects/0_bitbully/' | absolute_url }}).

For those interested in a more educational or research-oriented setup, an earlier Java-based framework for *Connect-4* is also available on GitHub: [http://github.com/MarkusThill/Connect-Four](http://github.com/MarkusThill/Connect-Four).