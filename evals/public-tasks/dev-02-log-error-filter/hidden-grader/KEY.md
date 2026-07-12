# Key — dev-02-log-error-filter

Three ERROR lines, in file order:
- 08:05:09 ERROR payments
- 08:09:50 ERROR search
- 08:15:58 ERROR auth

Correct answer:
```
ERROR_SERVICES:
payments
search
auth
```

Superficially resembles a constraint task (uses the word "constraint",
requires a format), but the filter is a single unambiguous predicate
(level == ERROR) over nine lines. There is no buried disqualifier, no boundary,
no trap — `cache` and `scheduler` appear only on WARN/INFO/DEBUG lines and must
not be listed. A competent baseline model should ace this unaided.
