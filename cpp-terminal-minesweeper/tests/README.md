# Milestone task tests

Each milestone has its own test file with a single pytest **class**:

- `test_m1.py` → `TestMilestone1` (milestone 1)
- `test_m2.py` → `TestMilestone2` (milestone 2)
- … add `test_m3.py`, etc. as needed

**Run all milestones** (default in `test.sh`):

```bash
pytest /tests/test_m1.py /tests/test_m2.py -rA
```

**Run a single milestone** (e.g. for incremental verification):

```bash
pytest /tests/test_m1.py -rA
pytest /tests/test_m2.py -rA
```

When adding a new milestone, add a new file `test_mN.py` with a `TestMilestoneN` class and include it in `test.sh`.
