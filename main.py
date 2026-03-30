from pawpal_system import Owner, Pet, Task, Schedule

# --- Create Owner ---
owner = Owner("Bob", "New Brunswick, New Jersey", "no late night tasks", 120)

# --- Create Pets ---
pet1 = Pet(name="Mochi", age=3, weight=20.0, species="dog", breed="Shiba Inu", gender="male")
pet2 = Pet(name="Luna", age=5, weight=10.0, species="cat", breed="Siamese", gender="female")

# --- Create Tasks ---
task1 = Task(name="Morning Walk",    description="Walk Mochi around the block",      due_date="today", duration=30,  priority="high")
task2 = Task(name="Feeding",         description="Feed both pets their morning meal", due_date="today", duration=10,  priority="high")
task3 = Task(name="Grooming",        description="Brush Luna's coat",                due_date="today", duration=20,  priority="medium")
task4 = Task(name="Playtime",        description="Play fetch with Mochi",            due_date="today", duration=45,  priority="low")
task5 = Task(name="Vet Medication",  description="Give Luna her daily medication",   due_date="today", duration=5,   priority="high")

# --- Build Schedule ---
schedule = Schedule(available_time=owner.available_time)
for task in [task1, task2, task3, task4, task5]:
    schedule.add_task(task)

plan = schedule.generate_plan()

# --- Print Today's Schedule ---
print("=" * 40)
print(f"  Today's Schedule for {owner.name}")
print(f"  Pets: {pet1.name} ({pet1.species}) & {pet2.name} ({pet2.species})")
print(f"  Available time: {owner.available_time} min")
print("=" * 40)

time_used = 0
for i, task in enumerate(plan, 1):
    print(f"{i}. [{task.priority.upper()}] {task.name} — {task.duration} min")
    print(f"   {task.description}")
    time_used += task.duration

print("-" * 40)
print(f"Total scheduled: {time_used} / {owner.available_time} min")

skipped = [t for t in schedule.tasks if t not in plan]
if skipped:
    print("\nSkipped (not enough time):")
    for t in skipped:
        print(f"  - {t.name} ({t.duration} min)")

print("=" * 40)
