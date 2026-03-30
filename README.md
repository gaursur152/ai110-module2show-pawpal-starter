# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

#### Testing PawPal +
python -m pytest
  Sorting (5 tests)
  - Shortest-first order is correct
  - Completed tasks are excluded from sort results
  - Empty schedule and single-task edge cases don't crash
  - All-same-duration tasks handled without error

  Recurrence (10 tests)
  - Daily advances exactly 1 day; weekly advances 7 days
  - No recurrence returns None
  - Next date is based on due_date, not today (drift prevention)
  - All metadata (name, duration, priority, pet, start_time) is copied to the new task  
  - Month and year boundary rollovers work correctly
  - complete_task() auto-appends the next occurrence to the schedule
  - Non-recurring tasks don't grow the schedule

  Conflict Detection (8 tests)
  - No conflicts when tasks have no start_time
  - Exact overlap and partial overlap report correct minutes
  - Back-to-back tasks (boundary touch) produce no conflict
  - Completed tasks are excluded
  - Same-pet vs different-pets label in conflict string
  - Non-overlapping tasks produce empty conflict list
  - Out-of-bounds index raises IndexError

  confidence level: 4
