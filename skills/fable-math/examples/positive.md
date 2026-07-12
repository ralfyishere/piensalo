# Positive example: the skill firing on a closed-form derivation

**Task:** find and justify a closed form for S(n) = 1 + 3 + 5 + ... + (2n-1). A "derive a closed form" ask - exactly the profile fable-math exists for.

1. Formalize: S(n) = sum_{k=1..n} (2k-1).
2. Small cases computed honestly: S(1)=1, S(2)=4, S(3)=9, S(4)=16, S(5)=25.
3. Conjecture: S(n) = n^2. Pattern extension alone is NOT accepted as proof - the whole point of the discipline is that patterns can break at the first uncomputed case.
4. Route A (algebraic): sum 2k - sum 1 = 2*n(n+1)/2 - n = n^2 + n - n = n^2.
5. Route B (independent, combinatorial): an n x n square decomposes into n L-shaped gnomons of sizes 1, 3, ..., 2n-1; hence the odd numbers tile n^2 exactly.
6. Routes agree; boundary probe n=0 gives S(0)=0=0^2 (empty sum) - holds.
7. Labeling: closed form n^2 is PROVED (two independent derivations); values for n<=5 are COMPUTED; no conjectured-only claims remain.

Why this is a hit: the conjecture was promoted to a result only after two genuinely different routes agreed and the boundary held, and every claim carries its evidence label (proved vs computed).
