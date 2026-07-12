<!-- Piénsalo worked example | label: DEMO | dir: coding -->

# Task

`shift_report.py` bills warehouse shifts. A shift that runs into the 22:00
night-rate window must bill its night portion at 1.5x. The test below fails;
fix the code.

```python
def night_minutes(start_min, end_min, night_start=1320):  # 1320 = 22:00
    if end_min > night_start:
        return end_min - night_start
    return 0
```

```python
def test_shift_ending_at_window_start():
    # 20:00-22:00 shift: ends exactly when night rate begins -> 0 night mins
    assert night_minutes(1200, 1320) == 0

def test_shift_crossing_window():
    # 21:00-23:00 shift: 60 night minutes
    assert night_minutes(1260, 1380) == 60

def test_shift_fully_inside_window():
    # 22:30-23:30 shift: all 60 minutes are night minutes  << FAILS
    assert night_minutes(1350, 1410) == 60
