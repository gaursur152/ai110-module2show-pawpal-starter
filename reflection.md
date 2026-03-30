# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Sort tasks by priority (high first), then picks tasks until you run out of  available time.
    - class owner  
        - attributes: name, address, avaliable_time, owners prefrence
        - method
            - create person
            - add person
            - edit person info
    - class pet
        - attributes: name, age, weight, type, breed, gender
        - method 
            - create pet
            - add pet
            - edit pet info
    - schedule( tasks, avliable_time)
        -take a lis of tasks and constrainsts
        - filters by priority
        output dailt plan
    -  class task
        - attributes : name, description, due date, duration, priority, completion status
        - mark completion



**b. Design changes**

  2. generate_plan() skips already-completed tasks — if a task is marked completed=True,
   it should probably be excluded from the plan. Right now it would still be scheduled. 
  3. edit_task has no bounds check — if you pass an invalid index, it will crash with an
   IndexError. Same for remove_task.
  4. Schedule is disconnected from Owner — available_time is duplicated in both Owner   
  and Schedule. When you wire up app.py, you'll need to remember to pass
  owner.available_time into Schedule. Consider just reading it from the owner directly. 

  Minor things:

  - Task.due_date is a plain string — fine for now, but easy to pass invalid values like
   "tomorrow". Not a blocker.
  - type is a built-in Python name — using it as an attribute on Pet works but shadows  
  the built-in. Consider renaming to species (which also matches the app.py starter code
   on line 44). 

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
