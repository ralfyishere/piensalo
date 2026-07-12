# Near-miss: the skill should NOT fire

**Task:** "Should I use JSON or YAML for this one config file?"

A small, fully reversible choice with well-known tradeoffs and negligible downside either way. Whatever is picked can be changed in minutes.

**Why firing would hurt:** building an objective hierarchy, causal graph, and scenario-weighted EV table for a two-option reversible call adds latency and manufactures filler analysis; a one-line tradeoff ("YAML for human-edited config, JSON if machines write it") answers faster and just as correctly.
