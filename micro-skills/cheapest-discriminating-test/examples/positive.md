# Positive example

**Debugging task:** builds fail intermittently on one machine. Three live hypotheses: H1 cache corruption, H2 stale antivirus signature, H3 disk pressure.

**Trigger present:** multiple competing hypotheses, and each candidate test (rebuild, snapshot restore) costs real minutes.

**Procedure applied:**
- Fingerprints written: only H1 predicts failure travels with the cache directory; only H2 predicts failure tracks the AV signature version; H3 predicts failure correlates with free-space dips regardless of both.
- Unifying discriminant: restore the machine snapshot twice — run A keeps the cache but resets AV; run B keeps AV but wipes the cache.
- Discrimination table committed BEFORE running:

| Run A | Run B | Verdict |
|---|---|---|
| fails | passes | H1 killed; H2 confirmed |
| passes | fails | H1 confirmed; H2 killed |
| fails | fails | H3 promoted; H1/H2 insufficient alone |
| passes | passes | none separated — escalate to disk-pressure replay |

**Required output produced:**
The table above plus the cost rationale: two runs discriminate three hypotheses; the rejected alternative (per-hypothesis logging: three runs that decide nothing) fails the discrimination test.
