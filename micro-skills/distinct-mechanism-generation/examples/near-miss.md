# Near-miss example — single known-correct answer exists

**Task:** "The build fails with `ImportError: No module named 'requests'`. What's the cause?"

The error names its own cause: the dependency is not installed in the build environment. This matches the "single known-correct answer exists" counterindication — the skill must NOT fire.

**Why firing would hurt:** Generating five "distinct mechanisms" for a solved diagnosis (cosmic-ray bit flip? shadowed module?) is enumeration theater — it delays the one-line fix, spends the token budget on noise, and trains the reader to skim past candidate lists.
