# Verification criteria

Domain verification criteria. Deterministic criteria are checked mechanically; adversarial criteria require constructing probes; evidence criteria grade support quality. Disqualifying criteria fail the whole candidate.

## Domain: software
### tests_pass_with_quoted_output (deterministic) [disqualifying]
Per live-state-truth and debugging-playbook: run the relevant test suite and quote the ACTUAL output — 'should work now' is a prediction, not a result. The candidate must contain real captured test output, not a claim that tests would pass.
- Tool protocol: `regex:(?i)(\d+\s+(tests? )?passed|all tests pass(ed)?|\bOK\b|exit (code )?0|PASSED)`

### hidden_case_probe (adversarial)
Per adversarial-verify's edge-case attack: construct at least three inputs the author visibly did NOT test — empty/zero, boundary (max size, off-by-one), and malformed/hostile — and predict the behavior before executing. Any surprise is a finding; a probe whose outcome you couldn't predict wrong is an activity, not a test.
- Tool protocol: `Execute each probe input against the candidate code; record input | prediction | actual | verdict rows.`

### scope_diff_clean (deterministic) [disqualifying]
Per scope-fence and change-control: the diff touches only files and behavior named or implied by the task. Compare the changed-file list against the task's scope; every out-of-scope change is either reverted or explicitly flagged in an 'Out of scope — noted:' block, never silently included.
- Tool protocol: `cmd:git diff --stat — compare changed paths against task scope; not runnable from candidate text alone`

### regression_guard (deterministic) [disqualifying]
Per debugging-playbook's regression_test verifier: the previously-passing suite must still pass, and a new regression test encodes the fixed behavior so it cannot silently return — the regression test must fail on the pre-fix code. Quote both runs per live-state-truth.
- Tool protocol: `regex:(?i)(regression test|repro(duction)?.{0,40}passes|no previously.{0,15}(green|passing).{0,20}(red|fail)|suite still (green|passes))`

### interface_compatibility (evidence)
Per change-control and verification-discipline: enumerate every public interface the change touches (signatures, CLI flags, file formats, API contracts) and show evidence each caller/consumer still works or that the break is documented with a migration path. 'Nothing else uses this' is an assumption until grepped.
- Tool protocol: `grep for each changed public symbol across the repo; list callers and their status.`

### Adversarial tests
- Feed the empty/zero-length input and the maximum-size input; predict before running (adversarial-verify).
- Run the test suite on the PRE-change code: any 'new' test that already passes proves nothing (empirical-validation: the experiment must be able to falsify).
- Grep for callers of every changed public symbol; try to find one the author missed.
- Revert the fix and re-run the reproduction: if it still passes, the fix is not the cause (debugging-playbook toggle test).

### Disqualifiers
- Any claim of passing tests without quoted execution output.
- The regression test passes even without the fix applied.
- Silent out-of-scope changes in the diff.
- A previously-green test is now red.
