# Near-miss example — user rescoped the questions mid-session

**Task history:** The user first asked "1) Why is the test flaky? 2) How much would parallelizing the suite cost? 3) Which CI provider should we switch to?" — then, two messages later: "Forget 2 and 3, just tell me why the test is flaky."

The original three-question list would trigger the skill, but the user withdrew two questions — the "rescoped mid-session, latest instruction wins" counterindication. The skill must NOT fire on the original list.

**Why firing would hurt:** Mapping and re-answering the withdrawn cost and CI-provider questions directly contradicts the user's latest instruction — it re-imports scope the user explicitly cut and pads the reply with answers nobody wants.
