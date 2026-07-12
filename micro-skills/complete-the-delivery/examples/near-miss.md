# Near-miss example (must NOT fire)

**Case:** the original request was "refactor the parser, add tests, and update the changelog" — but mid-task the user says "actually, skip the changelog and tests, just get the parser refactor in."

**Why it must not fire on the dropped parts:** the user explicitly rescoped the task (counterindication: the latest instruction supersedes). The remaining request is a single deliverable with no sub-parts.

**Why firing would hurt:** a checklist that lists tests and changelog as "NOT delivered" flags abandoned work as missing, second-guesses an explicit user decision, and pressures the session into re-doing work the user just cancelled.
