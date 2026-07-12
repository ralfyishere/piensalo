# Positive example — skill fires and repairs the output

**Task:** "Checkout abandonment is 40%, way above our 25% target. Propose fixes to the checkout flow."

**Trigger appears:** A named metric with a threshold comparison ("40% abandonment" vs a 25% target) is presented as ground truth, and the requested action (redesign the flow) hangs entirely on the number.

**Procedure applied:**
1. Load-bearing numbers: abandonment rate 40%; denominator = "checkout sessions"; window = last 30 days.
2. Artifact hypothesis: the number is wrong because sessions that complete payment via the external wallet redirect never fire the completion event — benign completions are being counted as abandonments.
3. Cheapest instrument probe, sequenced first: pull 20 "abandoned" sessions and check payment records for matching completed orders; separately, histogram abandonment by payment method.
4. Flip test: if the true rate were ~28% instead of 40%, the response changes from "redesign the flow" to "tune one step" — so the probe is mandatory.

**Required output produced:**

> 1. **40% abandonment** — artifact hypothesis: wallet-redirect completions never fire the completion event, inflating abandonment. Probe (before any redesign): cross-check 20 "abandoned" sessions against payment records; histogram by payment method.
> 2. **Denominator (checkout sessions)** — artifact hypothesis: bot traffic counted in sessions. Probe: re-count with bot filter applied.
>
> Sequencing: run both probes first. If the corrected rate is still ≥35%, proceed to flow redesign; if it drops near target, fix the event instrumentation and re-baseline before touching the flow.
