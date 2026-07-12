# Positive example

**Task:** "Write up last week's outage for the customer newsletter."

**Trigger present:** the deliverable is addressed to customers — a consumer other than the requester, who will act on it without a chance to push back.

**Procedure applied:**
- Consumer: paying customers. Next action: decide whether to trust the service with their peak-season traffic.
- Constraints: no internal service names, no engineer names, roughly 150 words, and no promise that the fix is verified (the patch is deployed but the soak test finishes Friday).
- Downstream assertion check: draft v1 said "fully resolved" — customers would repeat that as fact. Rescoped to "we deployed a fix and are monitoring through the week."
- Author-serving content stripped: the internal codename for the affected relay and a paragraph of methodology detail.

**Required output produced:**
Consumer statement (customers deciding on trust), constraint list with per-item compliance (length: pass at 140 words; internal names: removed; verified-fix promise: rescoped), and every claim now survives downstream repetition.
