# Positive example: the skill firing on a claimed sorting fix

**Candidate:** a PR claiming "fixed the unstable sort in the leaderboard; all tests pass." A finished artifact about to be trusted - exactly the profile fable-verify exists for.

1. Domain: software. Disqualifier sweep: candidate claims tests pass but quotes no output -> potential disqualifier on the quoted-output criterion; proceed to check rather than trust.
2. Deterministic: ran the suite myself: `21 passed` (quoted). Criterion passes on execution, but the candidate text itself contained a prediction, not a result - noted as evidence-quality finding.
3. Adversarial probes (predicted before running): equal-score players (prediction: order by join date; actual: order flips between runs -> SURPRISE); empty leaderboard (prediction: []; actual: []); 10k ties (prediction: stable; actual: stable after the fix).
4. The surprise: the fix stabilized scores but not the equal-score tiebreak, which was the reported bug. Reproduced the original complaint against the fixed code: still reproduces.
5. Verdict table: quoted-output | deterministic | candidate quoted none | FAIL (disqualifying) ; regression-guard | deterministic | original repro still fails | FAIL. Overall: FAIL, with the two quoted findings. Not checked here: production data distribution (no access) - stated, not assumed.

Why this is a hit: a PR that read as done was caught by a predicted-before-run probe; the review graded rather than fixed, quoted its evidence, and stated what it could not check.
