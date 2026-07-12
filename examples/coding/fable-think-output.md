Reproducing before patching. The failing case is `night_minutes(1350, 1410)`:
`end_min (1410) > night_start (1320)`, so it returns `1410 - 1320 = 90`,
not 60. Expected 60.

**Root cause**, not just the symptom: the function computes the night
portion as `end - night_start`, i.e. it assumes every shift STARTS before
the window. The night portion is really the overlap of two intervals:
`[start, end] ∩ [night_start, ∞)`.

```python
def night_minutes(start_min, end_min, night_start=1320):
    return max(0, end_min - max(start_min, night_start))
```

Verification — all three given tests, plus the boundary cases the interval
form exposes:

| case | expr | got | want |
|---|---|---|---|
| ends at window start | `night_minutes(1200, 1320)` | 0 | 0 |
| crosses window | `night_minutes(1260, 1380)` | 60 | 60 |
| fully inside window | `night_minutes(1350, 1410)` | 60 | 60 |
| starts exactly at 22:00 | `night_minutes(1320, 1380)` | 60 | 60 |
| entirely before window | `night_minutes(600, 660)` | 0 | 0 |

Adding the two new boundary cases as regression tests:

```python
def test_shift_starting_at_window_start():
    assert night_minutes(1320, 1380) == 60

def test_shift_entirely_before_window():
    assert night_minutes(600, 660) == 0
```

Ran the suite: 5 passed. One caveat left unverified: shifts that wrap past
midnight (`end_min > 1440`) are out of scope of the given tests and this
function still doesn't handle them — flagging, not silently "fixing".
