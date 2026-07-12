# Positive example — grant application against submission rules

**Task:** Finalize a grant application. The call for proposals states: "Applications must include a budget table and a two-page project summary. Applications exceeding 2 pages for the summary, or missing the budget table, will not be considered. PDF only."

**Trigger appears:** Explicit rejection conditions ("will not be considered") — the answer can fail outright regardless of writing quality.

**Procedure applied:**
1. Disqualifier list, each traced to the call text:
   - D1: budget table present ("missing the budget table ... will not be considered")
   - D2: project summary ≤ 2 pages ("exceeding 2 pages ... will not be considered")
   - D3: file format is PDF ("PDF only")
2. Check against the draft:
   - D1 — **HIT**: no budget table anywhere in the draft (evidence: document contains no table and no section titled "Budget").
   - D2 — pass: summary measures 1.8 pages.
   - D3 — not-checkable from the text; flagged for the export step.
3. D1 repaired before shipping: budget table added from the project cost sheet.

**Required output produced (placed before the completion claim):**

| Disqualifier | Source clause | Result |
|---|---|---|
| Budget table included | "missing the budget table ... will not be considered" | HIT → fixed (table added) |
| Summary ≤ 2 pages | "exceeding 2 pages ... will not be considered" | pass (1.8 pages) |
| PDF format | "PDF only" | not-checkable pre-export; flagged |

Completion claim scoped: "Swept D1–D3; D1 fixed, D3 must be verified at export."
