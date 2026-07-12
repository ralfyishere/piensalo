# Near-miss example — skill must NOT fire

**Task:** "Rename the private helper `parse_row_v2` to `parse_row` inside this one module. A repo-wide search confirms it has no callers outside the module and no dynamic references."

**Why it must not fire:** This matches a counterindication: the change is verified — not presumed — to have no dependents or adapting agents. Nothing outside the module can notice the rename, so there is no adaptation to trace.

**Why firing would hurt:** Manufacturing an adaptation story for a verified-local rename produces speculative filler, delays a ten-second edit, and trains readers to skim past second-order sections — eroding the skill's credibility for the changes where adaptation analysis actually matters.
