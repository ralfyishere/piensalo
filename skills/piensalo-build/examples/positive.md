# Positive example: the skill firing on an intermittent pagination bug

**Symptom (verbatim):** "GET /items?page=2 sometimes repeats the last item of page 1." An intermittent, user-visible bug - exactly the profile piensalo-build exists for.

1. Reproduction: seeded DB with 25 rows, page size 10; repeat-fetch loop reproduces 3/50 runs -> flaky, suspect ordering.
2. Symptom vs cause: duplicate item is the symptom; candidate causal layers: SQL ordering, offset math, concurrent inserts.
3. Hypotheses (ranked): H1 non-deterministic ORDER BY on equal timestamps; H2 off-by-one in OFFSET; H3 insert race between page fetches.
4. Discriminating tests: H2 predicts the bug is deterministic (it is not -> H2 killed). Freeze inserts: bug persists -> H3 killed. Add unique tiebreaker to ORDER BY: bug gone in 500 runs -> H1 confirmed.
5. Minimal fix: `ORDER BY created_at, id` (one line); no drive-by refactors - noted the missing index out of scope.
6. Regression proof (quoted): `pytest tests/test_pagination.py -q` -> `3 passed`; new test `test_stable_order_equal_timestamps` fails on pre-fix code, passes post-fix; full suite `142 passed`.
7. Evidence table: H1 | tiebreaker test | bug disappears | disappears | CONFIRMED. Residual assumption: production DB collation matches test DB (labeled, unverified).

Why this is a hit: each hypothesis was killed or confirmed by a test with different predicted outcomes, the fix stayed one line, and every "passes" claim carries quoted output.
