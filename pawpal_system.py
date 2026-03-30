from dataclasses import dataclass
from typing import List


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

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True


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
