from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from datetime import date, timedelta
from itertools import combinations


def _fmt_time(minutes: int) -> str:
    """Convert an integer number of minutes from midnight to a readable time string.

    Args:
        minutes: Minutes elapsed since midnight (e.g. 480 = 8:00 AM, 750 = 12:30 PM).

    Returns:
        A formatted string in 12-hour clock notation, e.g. '8:00 AM' or '12:30 PM'.
    """
    h, m = divmod(minutes, 60)
    period = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {period}"


@dataclass
class Conflict:
    """Represents a scheduling conflict between two overlapping tasks.

    Attributes:
        task_a:          The first conflicting Task.
        task_b:          The second conflicting Task.
        overlap_minutes: How many minutes the two task windows overlap.
    """

    task_a: "Task"
    task_b: "Task"
    overlap_minutes: int

    def __str__(self) -> str:
        """Return a human-readable warning describing the conflict.

        Includes both task names, their pet assignments, their start times,
        their durations, the overlap length, and whether the conflict is between
        tasks for the same pet or different pets.

        Returns:
            A formatted warning string, e.g.:
            "CONFLICT (different pets): 'Morning Walk' [Mochi] (8:00 AM, 30 min)
             overlaps 'Vet Medication' [Luna] (8:20 AM, 10 min) by 10 min"
        """
        a, b = self.task_a, self.task_b
        label_a = f"'{a.name}'" + (f" [{a.pet_name}]" if a.pet_name else "")
        label_b = f"'{b.name}'" + (f" [{b.pet_name}]" if b.pet_name else "")
        same_pet = a.pet_name and a.pet_name.lower() == b.pet_name.lower()
        scope = "same pet" if same_pet else "different pets"
        return (
            f"CONFLICT ({scope}): {label_a} "
            f"({_fmt_time(a.start_time)}, {a.duration} min) overlaps "
            f"{label_b} ({_fmt_time(b.start_time)}, {b.duration} min) "
            f"by {self.overlap_minutes} min"
        )



@dataclass
class Pet:
    name: str
    age: int
    weight: float
    species: str    # e.g. "dog", "cat"
    breed: str
    gender: str


@dataclass
class Task:
    name: str
    description: str
    due_date: str       # e.g. "2026-03-29"
    duration: int       # minutes
    priority: str       # "high", "medium", "low"
    completed: bool = False
    pet_name: str = ""        # which pet this task belongs to; "" means unassigned
    recurrence: str = ""      # "" (none), "daily", or "weekly"
    start_time: Optional[int] = None  # minutes from midnight (e.g. 480 = 8:00 AM); None = unscheduled

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as completed and generate the next occurrence if recurring.

        Sets self.completed = True. If the task has a recurrence of 'daily' or
        'weekly', calculates the next due date by adding 1 day or 7 days to the
        original due_date (not today), which prevents schedule drift when tasks
        are completed late.

        Returns:
            A new Task with the same attributes but completed=False and an
            updated due_date, if the task recurs. Returns None for one-off tasks.
        """
        self.completed = True

        if self.recurrence not in ("daily", "weekly"):
            return None

        # Parse due_date; treat "today" as today's date
        try:
            base = date.fromisoformat(self.due_date)
        except ValueError:
            base = date.today()

        delta = timedelta(days=1) if self.recurrence == "daily" else timedelta(weeks=1)
        next_due = (base + delta).isoformat()

        return Task(
            name=self.name,
            description=self.description,
            due_date=next_due,
            duration=self.duration,
            priority=self.priority,
            completed=False,
            pet_name=self.pet_name,
            recurrence=self.recurrence,
            start_time=self.start_time,
        )


class Owner:
    def __init__(self, name: str, address: str, preferences: str = "", available_time: int = 120):
        """Initialize an Owner with contact info, preferences, and available time in minutes."""
        self.name = name
        self.address = address
        self.preferences = preferences  # e.g. "no early morning tasks"
        self.available_time = available_time  # minutes available today

    def edit_info(self, name: str = None, address: str = None, preferences: str = None, available_time: int = None):
        """Update any combination of owner fields; omitted fields remain unchanged."""
        if name is not None:
            self.name = name
        if address is not None:
            self.address = address
        if preferences is not None:
            self.preferences = preferences
        if available_time is not None:
            self.available_time = available_time


class Schedule:
    def __init__(self, available_time: int):
        """Initialize a Schedule with an empty task list and a time budget in minutes."""
        self.tasks: List[Task] = []
        self.available_time = available_time  # total minutes available

    def add_task(self, task: Task):
        """Append a task to the schedule's task list."""
        self.tasks.append(task)

    def edit_task(self, index: int, updated_task: Task):
        """Replace the task at the given index with an updated Task object."""
        if index < 0 or index >= len(self.tasks):
            raise IndexError(f"No task at index {index}")
        self.tasks[index] = updated_task

    def remove_task(self, index: int):
        """Remove the task at the given index from the schedule."""
        if index < 0 or index >= len(self.tasks):
            raise IndexError(f"No task at index {index}")
        self.tasks.pop(index)

    def complete_task(self, index: int) -> Optional[Task]:
        """Mark the task at the given index complete and auto-append its next occurrence.

        Calls mark_complete() on the task. If the task is recurring ('daily' or
        'weekly'), the returned next-occurrence Task is appended to self.tasks so
        the owner does not need to manually re-add it.

        Args:
            index: Zero-based index of the task to complete.

        Returns:
            The newly created next-occurrence Task if the task recurs, or None
            if the task is a one-off.

        Raises:
            IndexError: If index is out of range.
        """
        if index < 0 or index >= len(self.tasks):
            raise IndexError(f"No task at index {index}")

        next_task = self.tasks[index].mark_complete()
        if next_task is not None:
            self.tasks.append(next_task)
        return next_task

    def detect_conflicts(self) -> List[Conflict]:
        """Detect scheduling conflicts between all pairs of timed, incomplete tasks.

        Uses itertools.combinations to evaluate every unique task pair exactly once.
        Two tasks conflict when their time windows overlap:
            overlap = min(a_end, b_end) - max(a_start, b_start) > 0

        Tasks without a start_time (unscheduled) and completed tasks are excluded.
        Conflicts are reported for both same-pet and cross-pet overlaps.

        Returns:
            A list of Conflict objects, each describing the two conflicting tasks
            and the number of minutes they overlap. Returns an empty list if no
            conflicts are found.
        """
        timed = [t for t in self.tasks if not t.completed and t.start_time is not None]
        conflicts = []
        for a, b in combinations(timed, 2):
            overlap = min(a.start_time + a.duration, b.start_time + b.duration) - max(a.start_time, b.start_time)
            if overlap > 0:
                conflicts.append(Conflict(task_a=a, task_b=b, overlap_minutes=overlap))
        return conflicts

    def filter_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Return tasks filtered by completion status and/or pet name.

        Args:
            completed: If True, return only completed tasks. If False, return only
                       incomplete tasks. If None, completion status is not filtered.
            pet_name:  If provided, return only tasks assigned to that pet (case-insensitive).
                       If None, pet name is not filtered.

        Returns:
            List of Task objects matching all supplied criteria.
        """
        result = self.tasks
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if pet_name is not None:
            result = [t for t in result if t.pet_name.lower() == pet_name.lower()]
        return result

    def sort_by_time(self) -> List[Task]:
        """Return incomplete tasks sorted by duration, shortest first.

        Uses a Shortest-Job-First (SJF) strategy: by scheduling the quickest
        tasks first, the owner can complete the maximum number of tasks before
        running out of available time.

        Returns:
            A list of incomplete Task objects sorted by duration ascending.
            Completed tasks are excluded.
        """
        incomplete = [t for t in self.tasks if not t.completed]
        return sorted(incomplete, key=lambda t: t.duration)

    def generate_plan(self) -> List[Task]:
        """Return a priority-sorted list of incomplete tasks that fit within available time."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        incomplete = [t for t in self.tasks if not t.completed]
        sorted_tasks = sorted(incomplete, key=lambda t: priority_order.get(t.priority, 99))

        plan = []
        time_used = 0
        for task in sorted_tasks:
            if time_used + task.duration <= self.available_time:
                plan.append(task)
                time_used += task.duration

        return plan


def build_plan(owner_name: str, preferences: str, available_time: int,
               pet_name: str, species: str,
               tasks: List[Task]):
    """Create Owner, Pet, and Schedule objects then return the generated plan."""
    owner = Owner(name=owner_name, address="", preferences=preferences, available_time=available_time)
    pet = Pet(name=pet_name, age=0, weight=0.0, species=species, breed="", gender="")
    schedule = Schedule(available_time=owner.available_time)
    for task in tasks:
        schedule.add_task(task)
    plan = schedule.generate_plan()
    return owner, pet, schedule, plan
