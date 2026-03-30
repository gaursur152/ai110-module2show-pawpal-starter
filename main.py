from datetime import date
from pawpal_system import Owner, Pet, Task, Schedule

TODAY = date.today().isoformat()

# --- Create Owner ---
owner = Owner("Bob", "New Brunswick, New Jersey", "no late night tasks", 120)

# --- Create Pets ---
pet1 = Pet(name="Mochi", age=3, weight=20.0, species="dog", breed="Shiba Inu", gender="male")
pet2 = Pet(name="Luna",  age=5, weight=10.0, species="cat", breed="Siamese",   gender="female")

# --- Create Tasks (added out of order: long durations mixed with short ones) ---
task1 = Task(name="Grooming",       description="Brush Luna's coat",                 due_date=TODAY, duration=20, priority="medium", pet_name="Luna",  recurrence="weekly")
task2 = Task(name="Playtime",       description="Play fetch with Mochi",             due_date=TODAY, duration=45, priority="low",    pet_name="Mochi", recurrence="")
task3 = Task(name="Vet Medication", description="Give Luna her daily medication",    due_date=TODAY, duration=5,  priority="high",   pet_name="Luna",  recurrence="daily")
task4 = Task(name="Morning Walk",   description="Walk Mochi around the block",       due_date=TODAY, duration=30, priority="high",   pet_name="Mochi", recurrence="daily")
task5 = Task(name="Feeding",        description="Feed both pets their morning meal", due_date=TODAY, duration=10, priority="high",   pet_name="",      recurrence="daily")

# Mark one task complete manually (no recurrence) to demonstrate filtering
task1.mark_complete()

# --- Build Schedule ---
schedule = Schedule(available_time=owner.available_time)
for task in [task1, task2, task3, task4, task5]:
    schedule.add_task(task)

# ── 1. sort_by_time ───────────────────────────────────────────────────────────
print("=" * 45)
print("  sort_by_time()  —  shortest job first")
print("=" * 45)
for t in schedule.sort_by_time():
    status = "x" if t.completed else " "
    pet    = f" [{t.pet_name}]" if t.pet_name else ""
    print(f"  [{status}] {t.duration:>3} min  {t.name}{pet}")

# ── 2. filter_tasks: incomplete only ─────────────────────────────────────────
print()
print("=" * 45)
print("  filter_tasks(completed=False)  —  pending")
print("=" * 45)
for t in schedule.filter_tasks(completed=False):
    pet = f" [{t.pet_name}]" if t.pet_name else ""
    print(f"  [ ] {t.name}{pet}  ({t.priority})")

# ── 3. filter_tasks: completed only ──────────────────────────────────────────
print()
print("=" * 45)
print("  filter_tasks(completed=True)  —  done")
print("=" * 45)
done = schedule.filter_tasks(completed=True)
if done:
    for t in done:
        print(f"  [x] {t.name} [{t.pet_name}]  ({t.priority})")
else:
    print("  (none)")

# ── 4. filter_tasks: by pet name ─────────────────────────────────────────────
for pet_name in ("Mochi", "Luna"):
    print()
    print("=" * 45)
    print(f"  filter_tasks(pet_name='{pet_name}')  —  {pet_name}'s tasks")
    print("=" * 45)
    for t in schedule.filter_tasks(pet_name=pet_name):
        status = "x" if t.completed else " "
        print(f"  [{status}] {t.name}  ({t.duration} min, {t.priority})")

# ── 5. filter_tasks: combined — incomplete Luna tasks ────────────────────────
print()
print("=" * 45)
print("  filter_tasks(completed=False, pet_name='Luna')")
print("=" * 45)
combined = schedule.filter_tasks(completed=False, pet_name="Luna")
if combined:
    for t in combined:
        print(f"  [ ] {t.name}  ({t.duration} min, {t.priority})")
else:
    print("  (none — all Luna tasks are done)")

# ── 6. Original generate_plan ────────────────────────────────────────────────
plan = schedule.generate_plan()
print()
print("=" * 45)
print(f"  generate_plan()  —  fits in {owner.available_time} min")
print("=" * 45)
time_used = 0
for i, t in enumerate(plan, 1):
    pet = f" [{t.pet_name}]" if t.pet_name else ""
    print(f"  {i}. [{t.priority.upper()}] {t.name}{pet}  — {t.duration} min")
    time_used += t.duration
print(f"  Total: {time_used} / {owner.available_time} min")
skipped = [t for t in schedule.tasks if t not in plan and not t.completed]
if skipped:
    print("  Skipped:")
    for t in skipped:
        print(f"    - {t.name} ({t.duration} min)")
print("=" * 45)

# ── 7. Recurring tasks via complete_task() ───────────────────────────────────
print()
print("=" * 45)
print("  complete_task()  —  recurring auto-scheduling")
print("=" * 45)

recurring_indices = [
    i for i, t in enumerate(schedule.tasks)
    if t.recurrence in ("daily", "weekly") and not t.completed
]

for idx in recurring_indices:
    task = schedule.tasks[idx]
    print(f"\n  Completing: '{task.name}' (recurrence={task.recurrence})")
    next_task = schedule.complete_task(idx)
    if next_task:
        print(f"  -> Next occurrence added: '{next_task.name}' due {next_task.due_date}")
    else:
        print(f"  -> No recurrence, nothing added.")

print()
print("  All tasks after completing recurring ones:")
for t in schedule.tasks:
    status = "done" if t.completed else "todo"
    pet    = f" [{t.pet_name}]" if t.pet_name else ""
    recur  = f" ({t.recurrence})" if t.recurrence else ""
    print(f"  [{status}] {t.name}{pet}{recur}  — due {t.due_date}")
print("=" * 45)

# ── 8. detect_conflicts() ─────────────────────────────────────────────────────
#
#  Timeline being tested (minutes from midnight):
#
#  8:00 AM       8:30 AM        9:00 AM     9:20 AM
#  |-------------|              |-----------|
#  Morning Walk (Mochi, 30min)  Playtime (Mochi, 20min)  <- no overlap
#        |-----|
#        Vet Medication (Luna, 10min @ 8:20) <- CONFLICT with Morning Walk
#        |-----|
#        Feeding (unassigned, 10min @ 8:20)  <- CONFLICT with Morning Walk
#                                            <- CONFLICT with Vet Medication

print()
print("=" * 45)
print("  detect_conflicts()  —  overlap warnings")
print("=" * 45)

conflict_schedule = Schedule(available_time=120)
conflict_schedule.add_task(Task(
    name="Morning Walk",   description="Walk Mochi",      due_date=TODAY,
    duration=30, priority="high", pet_name="Mochi", start_time=480,  # 8:00–8:30
))
conflict_schedule.add_task(Task(
    name="Vet Medication", description="Luna's meds",     due_date=TODAY,
    duration=10, priority="high", pet_name="Luna",  start_time=500,  # 8:20–8:30 !! overlaps Walk
))
conflict_schedule.add_task(Task(
    name="Feeding",        description="Feed both pets",  due_date=TODAY,
    duration=10, priority="high", pet_name="",      start_time=500,  # 8:20–8:30 !! overlaps Walk + Meds
))
conflict_schedule.add_task(Task(
    name="Playtime",       description="Play with Mochi", due_date=TODAY,
    duration=20, priority="low",  pet_name="Mochi", start_time=540,  # 9:00–9:20  no overlap
))

print(f"\n  Tasks scheduled:")
for t in conflict_schedule.tasks:
    from pawpal_system import _fmt_time
    end = _fmt_time(t.start_time + t.duration)
    pet = f" [{t.pet_name}]" if t.pet_name else " [unassigned]"
    print(f"    {_fmt_time(t.start_time)} - {end}  {t.name}{pet}")

print()
conflicts = conflict_schedule.detect_conflicts()
print(f"  {len(conflicts)} conflict(s) found:\n")
if conflicts:
    for c in conflicts:
        print(f"  WARNING: {c}")
else:
    print("  No conflicts detected.")
print("=" * 45)
