"""Exploration of binary circular words whose n-windows are all distinct.

Every claim made in the blog post about these words is checked here.
"""
import json, time
from fractions import Fraction


def enumerate_words(n):
    """All de Bruijn words of order n, normalised to start with n zeros.

    The words are returned as bit lists of length 2**n; the search also
    counts the nodes it visits so that the pruning can be judged.
    """
    L = 1 << n
    words, w, seen = [], [0] * n, {0}
    stats = {"nodes": 0, "dead_ends": 0}

    def dfs(v, depth):
        stats["nodes"] += 1
        if depth == L:
            words.append(w[:L])          # the last n-1 bits wrap onto the leading zeros
            return
        extended = False
        for bit in ((0,) if depth >= L - n + 1 else (0, 1)):
            nv = ((v << 1) | bit) & (L - 1)
            if nv in seen:
                continue
            extended = True
            seen.add(nv)
            w.append(bit)
            dfs(nv, depth + 1)
            w.pop()
            seen.discard(nv)
        if not extended:
            stats["dead_ends"] += 1

    dfs(0, 1)
    return words, stats


def value(word):
    v = 0
    for b in word:
        v = (v << 1) | b
    return v


def normalise(word, n):
    """Rotate a cyclic word so that its all-zero window starts at position 0."""
    L = len(word)
    for s in range(L):
        if all(word[(s + i) % L] == 0 for i in range(n)):
            return [word[(s + i) % L] for i in range(L)]
    raise ValueError("no all-zero window")


def arborescences(m):
    """Spanning arborescences of B(2,m) rooted at vertex 0, by the matrix-tree theorem."""
    N = 1 << m
    idx = [v for v in range(N) if v != 0]
    pos = {v: i for i, v in enumerate(idx)}
    M = [[Fraction(0)] * len(idx) for _ in idx]
    for v in idx:
        M[pos[v]][pos[v]] = Fraction(2)
        for bit in (0, 1):
            u = ((v << 1) | bit) & (N - 1)
            if u != 0:
                M[pos[v]][pos[u]] -= 1
    det, k = Fraction(1), len(idx)
    for c in range(k):
        p = next((r for r in range(c, k) if M[r][c] != 0), None)
        if p is None:
            return 0
        if p != c:
            M[c], M[p] = M[p], M[c]
            det = -det
        det *= M[c][c]
        for r in range(c + 1, k):
            if M[r][c]:
                f = M[r][c] / M[c][c]
                for cc in range(c, k):
                    M[r][cc] -= f * M[c][cc]
    assert det.denominator == 1
    return int(det)


def lyndon_words(n):
    """All Lyndon words over {0,1} whose length divides n (Duval's algorithm)."""
    out, w = [], [-1]
    while w:
        w[-1] += 1
        m = len(w)
        if n % m == 0:
            out.append("".join(str(b) for b in w))
        while len(w) < n:
            w.append(w[-m])
        while w and w[-1] == 1:
            w.pop()
    return out


def granddaddy(n):
    """The lexicographically least de Bruijn word of order n."""
    return [int(c) for c in "".join(lyndon_words(n))]


def prefer_one(n):
    """Greedy construction: always append a 1 if the resulting window is new."""
    L = 1 << n
    w = [0] * n
    seen, v = {0}, 0
    while len(seen) < L:
        for bit in (1, 0):
            nv = ((v << 1) | bit) & (L - 1)
            if nv not in seen:
                seen.add(nv)
                w.append(bit)
                v = nv
                break
        else:
            break
    return w[:L]


report = {}
for n in (2, 3, 4, 5):
    t0 = time.time()
    words, stats = enumerate_words(n)
    dt = time.time() - t0
    L = 1 << n
    vals = sorted(value(w) for w in words)
    counts = [sum(w[i] for w in words) for i in range(L)]
    rev = [normalise(list(reversed(w)), n) for w in words]
    cpl = [normalise([1 - b for b in w], n) for w in words]
    vs = set(vals)
    report[n] = dict(
        n=n, L=L, count=len(words), formula=2 ** (2 ** (n - 1) - n),
        arborescences=arborescences(n - 1), S=sum(vals), seconds=dt,
        nodes=stats["nodes"], dead_ends=stats["dead_ends"],
        ones_per_word=sum(words[0]), min_val=vals[0], max_val=vals[-1],
        position_counts=counts,
        counts_palindromic=counts[n:] == counts[n:][::-1],
        reversal_closed=all(value(r) in vs for r in rev),
        complement_closed=all(value(c) in vs for c in cpl),
        reversal_fixed_points=sum(1 for w, r in zip(words, rev) if w == r),
        granddaddy_is_min=value(granddaddy(n)) == vals[0],
        prefer_one_is_max=value(prefer_one(n)) == vals[-1],
        max_is_reverse_of_min=None,
        S_from_counts=sum(c * (1 << (L - 1 - i)) for i, c in enumerate(counts)),
    )
    lo = min(words, key=value)
    report[n]["max_is_reverse_of_min"] = value(normalise(list(reversed(lo)), n)) == vals[-1]
    r = report[n]
    print(f"n={n} L={L:3d} M={r['count']:5d} (2^(2^(n-1)-n)={r['formula']:5d}) "
          f"arb(B(2,{n-1}))={r['arborescences']:5d} S={r['S']:15d} t={dt:.4f}s "
          f"nodes={r['nodes']} dead_ends={r['dead_ends']}")
    print(f"   min={r['min_val']} max={r['max_val']} ones/word={r['ones_per_word']} "
          f"palindromic={r['counts_palindromic']} rev_closed={r['reversal_closed']} "
          f"cpl_closed={r['complement_closed']} revfix={r['reversal_fixed_points']}")
    print(f"   granddaddy==min: {r['granddaddy_is_min']}  prefer_one==max: {r['prefer_one_is_max']}"
          f"  max==reverse(min): {r['max_is_reverse_of_min']}  S_from_counts_ok: {r['S_from_counts']==r['S']}")
    print(f"   counts: {counts}")

json.dump(report, open('tools/debruijn/data/explore.json', 'w'), indent=1)
print("\nn=3 words:", [("".join(map(str, w)), value(w)) for w in enumerate_words(3)[0]])
print("granddaddy(5) =", "".join(map(str, granddaddy(5))), value(granddaddy(5)))
print("lyndon(5) =", lyndon_words(5))


# ---------------------------------------------------------------------------
# A de Bruijn word of order 6 is exactly the magic constant needed for the
# multiplication trick that finds the index of an isolated set bit.
# ---------------------------------------------------------------------------
def debruijn_bitscan_check(word):
    n = 6
    C = value(word)                      # 64-bit constant
    table = {}
    for k in range(64):
        idx = ((C << k) & 0xFFFFFFFFFFFFFFFF) >> (64 - n)
        assert idx not in table, "not a de Bruijn word"
        table[idx] = k
    ok = all(table[((1 << k) * C & 0xFFFFFFFFFFFFFFFF) >> 58] == k for k in range(64))
    return C, ok, [table[i] for i in range(64)]


gd6 = granddaddy(6)
C, ok, tbl = debruijn_bitscan_check(gd6)
print(f"\ngranddaddy(6) = {''.join(map(str, gd6))}")
print(f"constant = 0x{C:016x}  bitscan works for all 64 powers of two: {ok}")
print("table =", tbl)
