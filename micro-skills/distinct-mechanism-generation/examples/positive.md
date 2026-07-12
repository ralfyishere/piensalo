# Positive example — diagnosing a sign-up conversion drop

**Task:** "Sign-up conversion dropped 18% last week. Brainstorm possible causes."

**Trigger appears:** "Brainstorm possible causes" — an enumeration request. A naive draft would produce paraphrases: "sign-up flow issues", "conversion problems", "funnel friction" — three wordings of the same symptom.

**Procedure applied:**
1. One-line mechanism claims generated until stall:
   1. New consent checkbox added Tuesday causes abandons via an extra required step on mobile.
   2. A/B test bucket misassignment causes the drop via traffic counted against a variant that no longer exists.
   3. Analytics tag broke on the confirmation page, so conversions still happen but stop being *recorded* (measurement wrong).
   4. A marketing campaign shifted the traffic mix toward low-intent visitors — both traffic volume and conversion move from a third factor.
   5. Email verification provider latency causes timeouts at the final step.
2. Pairwise distinctness: an initial "checkout form problems" candidate collapsed into #1 (same causal path, different wording).
3. Off-vocabulary scan produced #3 (measurement is wrong) and #4 (common cause) — neither "tag" nor "campaign" appears in the task text.
4. Top two deepened: #1 — why: deploy log shows the checkbox shipped the day the drop began; falsifying test: segment conversion by platform; if desktop dropped equally, #1 dies. #3 — why: recorded revenue didn't drop proportionally; falsifying test: compare recorded sign-ups against welcome-email sends.
5. Tail (#2, #4, #5) kept as one-liners; no credences demanded yet.

**Required output produced:** the numbered five-mechanism list above — pairwise distinct, top candidates carrying why + falsifying test, and at least one candidate (#3) with no lexical overlap with the task's wording.
