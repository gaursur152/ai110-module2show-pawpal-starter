import pytest
from pawpal_system import Task, Schedule


# --- helpers ---

def make_task(name="Task", duration=30, priority="medium", completed=False,
              pet_name="", recurrence="", due_date="2026-03-30", start_time=None):
    return Task(name=name, description="", due_date=due_date,
                duration=duration, priority=priority, completed=completed,
                pet_name=pet_name, recurrence=recurrence, start_time=start_time)


# --- existing tests ---

def test_mark_complete_changes_status():
    task = Task(name="Walk", description="Morning walk", due_date="today", duration=30, priority="high")
    task.mark_complete()
    assert task.completed == True


def test_adding_task_increases_count():
    schedule = Schedule(available_time=120)
    task = Task(name="Feeding", description="Feed the pet", due_date="today", duration=10, priority="medium")
    schedule.add_task(task)
    assert len(schedule.tasks) == 1


# ── SORTING ───────────────────────────────────────────────────────────────────

def test_sort_by_time_orders_shortest_first():
    s = Schedule(available_time=200)
    s.add_task(make_task("Long", duration=60))
    s.add_task(make_task("Short", duration=10))
    s.add_task(make_task("Mid", duration=30))
    result = s.sort_by_time()
    durations = [t.duration for t in result]
    assert durations == sorted(durations)


def test_sort_by_time_excludes_completed():
    s = Schedule(available_time=200)
    s.add_task(make_task("Done", duration=5, completed=True))
    s.add_task(make_task("Active", duration=20))
    result = s.sort_by_time()
    assert len(result) == 1
    assert result[0].name == "Active"


def test_sort_by_time_empty_schedule():
    s = Schedule(available_time=60)
    assert s.sort_by_time() == []


def test_sort_by_time_single_task():
    s = Schedule(available_time=60)
    s.add_task(make_task("Only", duration=15))
    result = s.sort_by_time()
    assert len(result) == 1


def test_sort_by_time_all_same_duration_no_crash():
    s = Schedule(available_time=200)
    for i in range(4):
        s.add_task(make_task(f"T{i}", duration=30))
    result = s.sort_by_time()
    assert len(result) == 4
    assert all(t.duration == 30 for t in result)


# ── RECURRENCE ────────────────────────────────────────────────────────────────

def test_daily_recurrence_advances_one_day():
    task = make_task(recurrence="daily", due_date="2026-03-30")
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == "2026-03-31"


def test_weekly_recurrence_advances_seven_days():
    task = make_task(recurrence="weekly", due_date="2026-03-30")
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == "2026-04-06"


def test_no_recurrence_returns_none():
    task = make_task(recurrence="")
    next_task = task.mark_complete()
    assert next_task is None


def test_recurrence_uses_original_due_date_not_today():
    # Completing a task that was due 5 days ago should still step from that date
    task = make_task(recurrence="daily", due_date="2026-03-25")
    next_task = task.mark_complete()
    assert next_task.due_date == "2026-03-26"  # not today + 1


def test_recurrence_preserves_all_metadata():
    task = make_task(name="Med", duration=15, priority="high", pet_name="Max",
                     recurrence="daily", due_date="2026-03-30", start_time=480)
    next_task = task.mark_complete()
    assert next_task.name == "Med"
    assert next_task.duration == 15
    assert next_task.priority == "high"
    assert next_task.pet_name == "Max"
    assert next_task.recurrence == "daily"
    assert next_task.start_time == 480
    assert next_task.completed == False


def test_recurrence_month_boundary():
    task = make_task(recurrence="daily", due_date="2026-03-31")
    next_task = task.mark_complete()
    assert next_task.due_date == "2026-04-01"


def test_recurrence_year_boundary():
    task = make_task(recurrence="weekly", due_date="2026-12-28")
    next_task = task.mark_complete()
    assert next_task.due_date == "2027-01-04"


def test_complete_task_appends_next_to_schedule():
    s = Schedule(available_time=120)
    s.add_task(make_task("Feed", recurrence="daily", due_date="2026-03-30"))
    s.complete_task(0)
    assert len(s.tasks) == 2
    assert s.tasks[1].due_date == "2026-03-31"
    assert s.tasks[1].completed == False


def test_complete_task_nonrecurring_does_not_grow_schedule():
    s = Schedule(available_time=120)
    s.add_task(make_task("One-off", recurrence=""))
    s.complete_task(0)
    assert len(s.tasks) == 1


# ── CONFLICT DETECTION ────────────────────────────────────────────────────────

def test_no_conflicts_when_no_start_times():
    s = Schedule(available_time=200)
    s.add_task(make_task("A", duration=60))
    s.add_task(make_task("B", duration=60))
    assert s.detect_conflicts() == []


def test_exact_overlap_detected():
    s = Schedule(available_time=200)
    s.add_task(make_task("A", duration=30, start_time=480))
    s.add_task(make_task("B", duration=30, start_time=480))
    conflicts = s.detect_conflicts()
    assert len(conflicts) == 1
    assert conflicts[0].overlap_minutes == 30


def test_partial_overlap_correct_minutes():
    s = Schedule(available_time=200)
    s.add_task(make_task("A", duration=60, start_time=480))   # 8:00–9:00
    s.add_task(make_task("B", duration=60, start_time=510))   # 8:30–9:30
    conflicts = s.detect_conflicts()
    assert len(conflicts) == 1
    assert conflicts[0].overlap_minutes == 30


def test_back_to_back_tasks_no_conflict():
    s = Schedule(available_time=200)
    s.add_task(make_task("A", duration=60, start_time=480))   # 8:00–9:00
    s.add_task(make_task("B", duration=30, start_time=540))   # 9:00–9:30
    assert s.detect_conflicts() == []


def test_completed_tasks_excluded_from_conflicts():
    s = Schedule(available_time=200)
    s.add_task(make_task("Done", duration=60, start_time=480, completed=True))
    s.add_task(make_task("Active", duration=60, start_time=480))
    assert s.detect_conflicts() == []


def test_conflict_same_pet_label():
    s = Schedule(available_time=200)
    s.add_task(make_task("A", duration=60, start_time=480, pet_name="Max"))
    s.add_task(make_task("B", duration=60, start_time=480, pet_name="Max"))
    conflicts = s.detect_conflicts()
    assert "same pet" in str(conflicts[0])


def test_conflict_different_pets_label():
    s = Schedule(available_time=200)
    s.add_task(make_task("A", duration=60, start_time=480, pet_name="Max"))
    s.add_task(make_task("B", duration=60, start_time=480, pet_name="Bella"))
    conflicts = s.detect_conflicts()
    assert "different pets" in str(conflicts[0])


def test_no_conflicts_non_overlapping_tasks():
    s = Schedule(available_time=500)
    s.add_task(make_task("A", duration=30, start_time=480))   # 8:00–8:30
    s.add_task(make_task("B", duration=30, start_time=540))   # 9:00–9:30
    s.add_task(make_task("C", duration=30, start_time=600))   # 10:00–10:30
    assert s.detect_conflicts() == []


def test_out_of_bounds_index_raises():
    s = Schedule(available_time=60)
    with pytest.raises(IndexError):
        s.complete_task(5)
    with pytest.raises(IndexError):
        s.remove_task(0)
