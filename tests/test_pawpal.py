from pawpal_system import Task, Schedule


def test_mark_complete_changes_status():
    task = Task(name="Walk", description="Morning walk", due_date="today", duration=30, priority="high")
    task.mark_complete()
    assert task.completed == True


def test_adding_task_increases_count():
    schedule = Schedule(available_time=120)
    task = Task(name="Feeding", description="Feed the pet", due_date="today", duration=10, priority="medium")
    schedule.add_task(task)
    assert len(schedule.tasks) == 1
