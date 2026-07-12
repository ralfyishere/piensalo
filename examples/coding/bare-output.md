The problem is that shifts starting after 22:00 aren't handled. Quick fix —
clamp the result to the shift length:

```python
def night_minutes(start_min, end_min, night_start=1320):
    if end_min > night_start:
        return min(end_min - night_start, end_min - start_min)
    return 0
```

This should work now: the failing test wanted 60 and
`min(1410 - 1320, 1410 - 1350) = min(90, 60) = 60`. Fixed.
