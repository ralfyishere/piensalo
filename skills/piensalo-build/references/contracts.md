# Repair contracts

Repair procedures distilled from curated expert reasoning traces. Referenced by id from references/failure-checks.md.

## RC-01-diagnose-the-ruler
**Trigger:** Any task where a metric, kill-list, KPI, or verdict is presented as ground truth and drives the next decision.

**Procedure:**
1. List every number the decision rests on (metric, LTV, threshold, window).
2. For each, write the artifact hypothesis: 'this number is wrong because <censoring / benign-case miscounting / denominator drift / stale input>'.
3. Design the cheapest check of the instrument itself (histogram against the cutoff, smoke-test the benign case, recompute the denominator) and run it BEFORE any fix.
4. If the instrument is broken, publish the corrected number before trusting any downstream A/B or kill decision.

**Failure it repairs:** Accepts the metric as reality and optimizes against it: proposes channel/feature fixes for a number that is partly measurement artifact; ships fixes that 'change nothing' because the ruler, not the system, produced the reading.

## RC-02-kills-close-hypotheses-not-spaces
**Trigger:** A closed verdict / kill-list exists, but live evidence contradicts it (a competitor succeeds, a symptom recurs, an outlier wins).

**Procedure:**
1. State the strongest live contradiction to the verdict in one sentence (who is succeeding at the 'impossible' thing).
2. Audit each kill: did it falsify the mechanism, or only one implementation/message/measurement of it?
3. Generate candidates from mechanism classes ABSENT from the kill-list (channels/causes that leave no footprint where you looked).
4. Attach a near-free discriminating test to each; sequence the tests that reshape everything else first.

**Failure it repairs:** Defends the closed verdict ('we already proved that doesn't work'), or reopens by re-running the killed experiments instead of generating new mechanism classes; treats the kill-list as covering the whole space when it only covers the tested points.

## RC-03-symptom-label-distrust
**Trigger:** An error message, log line, alert, or vendor explanation names its own cause ('rate limited', 'quota', 'timeout').

**Procedure:**
1. Trace the exact error string to the line that emits it; check whether its content is derived from the exception or hardcoded.
2. Collect the facts that should co-occur with the claimed cause (429s, quota usage, throttle headers) and check they actually do.
3. Correlate onset time with change events (releases, deploys, config) before accepting any steady-state explanation.
4. Reproduce the masked failure in isolation with real payloads before proposing the fix; separate the minimal fix from the amplifier (report, don't silently expand scope).

**Failure it repairs:** Takes the log at its word: investigates rate limits, adds backoff/retry logic, contacts the vendor about quota — a week-long goose chase against a label no code path ever computed.

## RC-04-unifying-discriminant
**Trigger:** Multiple open hypotheses/anomalies could each get their own test; budget allows only a few experiments.

**Procedure:**
1. Write each hypothesis's distinct observable fingerprint (what it predicts that the others do not).
2. Search for the manipulation under which the hypotheses predict DIFFERENT outcomes; prefer one that covers >=2 hypotheses.
3. Pre-commit a discrimination table: every possible result row -> which hypotheses it confirms, kills, or leaves untouched (include the 'no bucket dominates' row).
4. Reject any proposed test whose every outcome leaves the hypothesis set unchanged.

**Failure it repairs:** One test per hypothesis, usually confirmatory ('add logging', 'increase coverage'); tests whose outcomes are consistent with several hypotheses and therefore decide nothing; no pre-stated mapping from result to verdict.

## RC-05-breadth-without-depth-tax
**Trigger:** Open-ended generation tasks: enumerate causes, mechanisms, candidates, risks.

**Procedure:**
1. Enumerate mechanisms first as one-line claims until generation stalls; only then deepen.
2. Explicitly scan for 'the repo/system already demonstrates the fix for an adjacent case' candidates — these are the ones weaker models miss.
3. Deepen only the top-k candidates with mechanism/test detail; keep the tail as claims.
4. Cap per-candidate schema at generation time (claim/why/test); demand credences and discriminators only for finalists.

**Failure it repairs:** Trades breadth for depth (rich schema per candidate, fewer candidates) or depth for breadth (long shallow lists); systematically misses the mechanisms furthest from the evidence log's surface wording ('the fix pattern already exists in-repo, apply it here').

## RC-06-determinize-dont-rediscover
**Trigger:** A failure was caught by judgment/attention (a human or model noticed it), or the same correction has occurred twice.

**Procedure:**
1. Classify the failure: was it caught by pattern/script or by judgment? If judgment, ask what deterministic check would have caught it.
2. Prefer, in order: generate the artifact from source (drift impossible) > blocking validator in the pipeline (drift caught) > triggered skill/procedure > advisory note.
3. For any correction repeated twice in the same class, encode the invariant as a script/gate and retro-run it against the historical failure states to prove it would have fired.
4. Never spend always-on prompt budget on what a gate can enforce.

**Failure it repairs:** Absorbs corrections as prose (notes, docs, longer prompts); re-relies on vigilance for invariants that already failed under vigilance; adds always-on instructions that dilute attention instead of gates that execute.

## RC-07-completion-integrity
**Trigger:** Asked to confirm work is 'done' (release, migration, checklist) when some items are verified and others are not.

**Procedure:**
1. Partition claims into verified / unverified / failed — 'unverified' is its own category, never merged into either neighbor.
2. For each unverified item, state what was NOT checked and why the check is currently impossible.
3. Scope the risk to the consumer's actual promise: what does the next action (announcement, deploy, handoff) assert, and does the unverified item touch it?
4. Give the decision-maker a recommendation plus the condition under which it flips; commit to closing the open item and name when.

**Failure it repairs:** Rounds 9/10 up to 'done' (the script always worked before); or rounds down to 'blocked' and stalls the announcement; either way fails to map the unverified item onto the specific downstream promise it does or doesn't threaten.

## RC-08-live-state-over-plan-markers
**Trigger:** Resuming interrupted work from a handoff/plan document, or any artifact that claims to describe current state.

**Procedure:**
1. Enumerate every claim the handoff makes about current state; for each, name the live source that can confirm it (logs, crontab, DB, monitoring).
2. Verify the claims in blast-radius order: active incidents first, then 'done' items, then pending items.
3. Log every discrepancy between document and reality — including ones that don't change the plan — as verification-list items.
4. Once one marker is shown wrong, downgrade ALL of that document's markers to unverified.

**Failure it repairs:** Resumes from the plan's markers ('jobs 1-3 done, continue with 4'), compounding the dead session's ordering error; misses the offset anomaly because it doesn't block the literal task; acts on stale evidence when fresh evidence is one command away.

## RC-09-explicit-negative-space
**Trigger:** Producing a plan or fix in a high-blast-radius situation (data repair, live systems, irreversible actions).

**Procedure:**
1. For each planned action, ask which direction of error is cheaper given the system's actual detection/recovery machinery, and order operations to fail in the cheap direction.
2. Write the explicit NOT-do list: the attractive actions being declined, each with the failure mode it would create.
3. Preserve an undo path through every step (comment, don't delete; back up before repair); name the path.
4. Adjacent defects found en route go in a 'noticed, not fixed' block — reported, never silently fixed.

**Failure it repairs:** Plans state only positive actions; scope creeps into adjacent fixes; 'cleanup' runs before diagnosis (blind dedupe, killed processes, deleted rollback paths); error-cost asymmetry (gap vs duplicate, miss vs false-positive) is never computed.

## RC-10-mission-gradient-over-urgency
**Trigger:** Choosing the next action from a portfolio where urgent/visible/glamorous items compete with mission-central, burden-reducing, or time-windowed ones.

**Procedure:**
1. Score candidate actions on mission-centrality, info-gain, operator-burden reduction, and time-window perishability — not on urgency or visibility.
2. Check dependency structure first: an action that unblocks/gates others outranks isolated wins (keystone rule).
3. Treat perishable evidence (expiring access, closing windows) as a hard scheduling constraint that beats durable work.
4. Flag, separately from selection, any candidate whose execution requires approval — never let approval-need silently demote or promote it.

**Failure it repairs:** False urgency: picks the visible, novel, or 'on fire' item; builds dashboards/frameworks instead of capturing perishable evidence; never asks which action reduces recurring operator burden or gates the most downstream work.

## RC-11-saturation-recognition
**Trigger:** An eval/experiment where all arms score high and close together, or a fixture whose evidence 'enumerates its own gaps'.

**Procedure:**
1. Before interpreting arm differences, check the ceiling: if all arms cluster near the top, the fixture, not the arms, is the finding.
2. Apply the pre-registered decision rule verbatim; report favorable secondary observations but label them explicitly as not changing the verdict.
3. Classify the saturated instrument as development-only and block further replication spend on it.
4. Route effort to a discriminating instrument (harder fixture, held-out set) before any rerun; when a space is genuinely exhausted, switch from generation to applying known results.

**Failure it repairs:** Reads uniform high scores as 'everything works', or spends more replications on a task that cannot discriminate; rescues a losing arm by re-weighting post-hoc; keeps generating novel hypotheses when the space is exhausted instead of applying what is known.

## RC-12-credenced-foresight-with-instrumentation
**Trigger:** Committing to one of several strategic options whose costs arrive 5-20 decisions later.

**Procedure:**
1. Sketch each option as a trajectory: what breaks ~5, ~10, ~20 decisions out, with the mechanism.
2. Identify which constraint binds inside the decision window (often not the one the brief emphasizes).
3. Pre-register predictions: option, horizon date, claim, mechanism, credence, observable that scores it.
4. Separate instrument-now items (trends unrecoverable later, baselines that must be pre-registered) and start them immediately.
5. Commit; then price the cheapest hedge that converts the worst branch into a staged recovery — prefer hedges valuable on both branches.

**Failure it repairs:** Pro/con lists anchored on present constraints (capacity math) rather than which constraint binds within the decision window; predictions without dates, credences, mechanisms, or observables — so they can never be scored.

## RC-13-operational-semantics-ontology
**Trigger:** Designing artifacts that unify two concepts (one file/table/type for both) or assigning role-implying names (Engine, Ledger, Manager, Registry).

**Procedure:**
1. On repeated corrections, name the pattern at the level where all instances are the same error.
2. Before unifying concepts: fill the lifecycle table (created-when, update-rule, retired-when, who-acts-on-it); any differing column means separate artifacts or a written merge justification.
3. Before naming: expand the name's implied capabilities and point at the design element providing each; unmet claim means rename to actual function.
4. Choose the asset by execution moment: procedural + moment-bound failures become triggered procedures, not memory prose; validate the asset retroactively against the historical corrections.

**Failure it repairs:** Treats each correction as a one-off wording fix; merges concepts that co-occur; names components after the system they serve rather than what they do; stores the lesson as advisory prose that never executes at the shipping moment.

## RC-14-minimal-tool-footprint
**Trigger:** Task solvable from provided/named inputs; tools available.

**Procedure:**
1. Before each tool call, state (at least internally) which pending decision the result changes; skip calls whose every outcome leaves the answer unchanged.
2. Read the named load-bearing inputs completely, once; do not re-read to 'verify' what the harness already confirmed.
3. Check granted tools against the task's implied actions BEFORE starting; if the protocol implies execution you lack, say so and reason instead of burning turns on denied attempts.
4. Budget turns explicitly in bounded harnesses; reserve the final turn for output.

**Failure it repairs:** Tool churn that never changes the answer (re-reading, listing, exploratory greps as ritual); or the inverse — answering about state without reading it at all. Separately, harness mismatch: protocols implying execution without granting it kill high-initiative models on max-turns.

## RC-15-verdict-first-synthesis-from-failure
**Trigger:** Reporting the outcome of an experiment/attempt that failed, was interrupted, or contradicted the hoped-for result.

**Procedure:**
1. State the verdict first, applying any pre-registered rule literally.
2. Attribute causes with individual confidence levels; explicitly list considered-and-rejected causes.
3. Separate infrastructure/harness failures from subject failures; label invalid cells INVALID, never as weak performance.
4. Convert each supported cause into one concrete next change; record what the failure does NOT change (stop/resume confidence statement).

**Failure it repairs:** Buries the verdict under caveats or rescues it post-hoc; reports 'it failed' without cause attribution at stated confidence; conflates infrastructure failures (quota stubs, harness deaths, missing grants) with capability failures, poisoning the dataset for future decisions.

## RC-16-exemplar-transplant
**Trigger:** Attempting to transfer any of the above contracts to a weaker model via prompts/skills.

**Procedure:**
1. Pair every transferred contract with one full worked exemplar drawn from the curated expert reasoning traces, not a paraphrase.
2. Pre-register the gap-closed criterion before the transfer experiment.
3. Run the target model on a NON-saturated held-out fixture with and without the exemplar; grade blind.
4. Promote the transfer only if the pre-registered criterion is met; otherwise record the negative result.

**Failure it repairs:** Given only the abstract rule, the weaker model complies with the letter (produces a table, produces credences) without the selection judgment the exemplar demonstrates (which discriminant unifies, which column differs).
