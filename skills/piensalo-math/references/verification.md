# Verification criteria

Domain verification criteria. Deterministic criteria are checked mechanically; adversarial criteria require constructing probes; evidence criteria grade support quality. Disqualifying criteria fail the whole candidate.

## Domain: mathematics
### independent_derivation (judgment) [disqualifying]
Per verification-discipline (recompute any arithmetic independently) and adversarial-verify's independent-recomputation attack: re-derive the result by a DIFFERENT route than the candidate used — different method, different decomposition, or different starting identity. Agreement via the same route is replication of the same error, not verification.

### numerical_substitution (deterministic) [disqualifying]
Substitute at least two concrete numeric values (one ordinary, one awkward — negative, fractional, large) into both sides of every derived identity/equation and confirm equality to tolerance. Per verification-discipline: this is arithmetic and must be recomputed, not eyeballed. The candidate must show the substitution, not assert it.
- Tool protocol: `regex:(?i)(substitut|plug(ging)?\s+in|numerical(ly)?\s+(check|verif)|both sides|x\s*=\s*-?\d)`

### symbolic_check (deterministic)
Where a CAS applies, verify the manipulation symbolically (sympy simplify/expand of LHS-RHS to zero) rather than trusting hand algebra — per empirical-validation, run the cheapest experiment that could falsify instead of reasoning about whether it works. Quote the tool output per live-state-truth.
- Tool protocol: `tokens:any:sympy,symbolic,simplify,expand,identity holds,lhs - rhs`

### boundary_behavior (adversarial)
Per adversarial-verify's edge-case attack: evaluate the result at the domain's boundaries — 0, 1, infinity/limits, degenerate cases (empty set, n=0, singular matrix), and points where denominators, logs, or square roots blow up. Each boundary either behaves as the claim predicts or is an explicit stated exclusion.
- Tool protocol: `Evaluate the expression/claim at each boundary point; record point | predicted | actual.`

### counterexample_search (adversarial) [disqualifying]
Per adversarial-verify: actively try to disprove the claim before presenting it. For universal claims ('for all n', 'always converges'), search small cases exhaustively and randomized cases broadly for a counterexample. One counterexample kills the claim regardless of how elegant the proof reads; failure to find one after a REAL search is stated at its evidence level per verification-discipline ('no counterexample found for n ≤ 10^6' is honest; 'shown' is not).
- Tool protocol: `Brute-force small cases + randomized sampling; report the search space actually covered.`

### Adversarial tests
- Substitute an awkward value (negative, irrational, huge) the derivation's implicit assumptions might not survive.
- Attack the weakest inference step: find the exact line where the proof would break if a sign or quantifier flipped.
- Check whether the claim silently assumes positivity, integrality, commutativity, or convergence that was never established.
- Run the smallest case by hand (n=0, n=1) — hand-checkable cases catch more derivation bugs than re-reading the algebra.

### Disqualifiers
- A counterexample exists within the claimed domain.
- Numerical substitution disagrees on both sides of a claimed identity.
- Independent re-derivation reaches a different result and the discrepancy is unresolved.
- Arithmetic asserted without independent recomputation.
