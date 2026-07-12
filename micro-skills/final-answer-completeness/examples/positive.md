# Positive example — multi-question stakeholder email

**Task:** "Three things: 1) Did the migration finish? 2) What was the total downtime? Also tell me whether we need the maintenance window on Saturday — yes or no first, please. 3) List the follow-up items as bullets."

**Trigger appears:** Numbered questions, a buried "also tell me..." directive, and two shape directives ("yes or no first", "as bullets"). A draft exists that answers 1 and 3 but skips the Saturday question and answers 2 inside a paragraph.

**Procedure applied:**
1. Extracted items: Q1 migration finished? Q2 total downtime? Q2b Saturday window needed — yes/no first. Q3 follow-ups as bullets.
2. Mapping against the draft: Q1 → paragraph 1 (answered). Q2 → paragraph 2 (answered, but buried). Q2b → **unmapped**. Q3 → bullet list (answered, correct shape).
3. Q2b answered now, yes/no first: "No — the migration completed, so the Saturday window can be released."
4. Shape check: Q2 promoted to a direct figure up front ("Total downtime: 14 minutes"); Q2b now leads with "No".
5. No machine-parsed lines mandated; rule 5 not applicable.
6. First two sentences now carry the primary answers, not preamble.

**Required output produced (3+ questions, so mapping included):**
- Q1 finished? → sentence 1 ("Yes, the migration completed at 02:10 UTC.")
- Q2 downtime? → sentence 2 ("Total downtime: 14 minutes.")
- Q2b Saturday window? → paragraph 2, yes/no first ("No — ...")
- Q3 follow-ups → bullet list at the end.
