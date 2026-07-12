# Positive example

**Inputs (ops handoff):** the handoff doc says "migration jobs 1–3 complete." The live crontab has no entry for job 3. An alert log shows job 3 fired once at 02:15.

**Trigger present:** a document's claim disagrees with observed live state for the same quantity (job 3's status).

**Procedure applied:**
1. Conflict stated: doc claims job 3 complete; crontab shows job 3 never installed (doc vs. live state).
2. Classification: source stale or wrong.
3. Rule applied and named: live state beats documents — job 3 treated as NOT installed. The 02:15 firing traced to a different host: a second conflict, logged separately.
4. Downgrade: the doc's "jobs 1–2 complete" markers are now unverified; each gets re-checked against the crontab before the migration resumes.

**Required output produced:**
A contradiction log with both conflicts (one sentence, sources named, classification, rule applied), plus the caveat that every "complete" marker from the handoff doc is unverified until re-checked.
