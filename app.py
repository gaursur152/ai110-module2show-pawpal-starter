import streamlit as st
from pawpal_system import Owner, Pet, Task, Schedule, build_plan  # [ADDED]

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
# [ADDED] extra owner/pet fields needed by our classes
preferences = st.text_input("Owner preferences", value="no early morning tasks")
available_time = st.number_input("Available time today (minutes)", min_value=10, max_value=480, value=120)

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "task_objects" not in st.session_state:  # [ADDED] initialize Task object list
    st.session_state.task_objects = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority}
    )
    # [ADDED] also store as real Task objects for the scheduler
    st.session_state.task_objects.append(
        Task(name=task_title, description="", due_date="today", duration=int(duration), priority=priority)
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )

    # [ADDED] call build_plan from pawpal_system.py
    task_objects = st.session_state.get("task_objects", [])
    if task_objects:
        owner, pet, schedule, plan = build_plan(
            owner_name=owner_name, preferences=preferences, available_time=int(available_time),
            pet_name=pet_name, species=species, tasks=task_objects
        )

        st.divider()
        st.success(f"Daily plan for {owner.name} & {pet.name} ({int(available_time)} min available)")
        time_used = 0
        for i, task in enumerate(plan, 1):
            st.markdown(f"**{i}. {task.name}** — {task.duration} min | Priority: `{task.priority}`")
            time_used += task.duration
        st.info(f"Total time scheduled: {time_used} / {int(available_time)} min")

        skipped = [t for t in task_objects if t not in plan]
        if skipped:
            st.warning("Skipped (not enough time): " + ", ".join(t.name for t in skipped))
