---
name: plan
description: >
  Plan a sprint: produce a sprint index (sprint.md) and individual task files from a goal or
  context. Human reviews and adjusts before execution begins.
tools:
  - Read
  - Write
  - Glob
compatibility:
  agents: all
---

# /plan

Plan a sprint from a goal, a context file, or the current project state.

**Usage:**
```
/plan "add JWT authentication"
/plan --context spec.md
/plan                           # reads CLAUDE.md and current .loops/sprint.md if present
```

## What You Produce

Two things:

**1. `.loops/sprint.md`** — the sprint index. Ordered task list with dependencies, sprint goal,
and metadata. This is what the loop runner reads to decide what's next. It is also the human's
status dashboard.

**2. `.loops/tasks/task-NNN.md`** — one file per task. Full execution context: specific
instructions, relevant file paths and function signatures the worker will need, and clear done
criteria. Each task file is self-contained — a worker reading only that file and CLAUDE.md
should have everything needed to execute.

## Sprint Index Format

```yaml
---
id: sprint-001
title: "Brief sprint name"
status: pending
goal: "One sentence: what does this sprint accomplish for a user?"
approved: false
eval: ""
summary: ""
---

## Tasks

- [ ] task-001: Brief task title
- [ ] task-002: Brief task title [depends: task-001]
- [ ] task-003: Brief task title [depends: task-001]
- [ ] task-004: Brief task title [depends: task-002, task-003]
```

Dependencies use `[depends: task-NNN, ...]` inline. Tasks with no `depends` are immediately
runnable.

## Task File Format

```yaml
---
id: task-001
title: "Brief task title"
status: pending
depends: []
done_criteria:
  - Specific, verifiable criterion
  - Another criterion
summary: ""
attempts: 0
isolation: true
---

## Instructions

[Specific instructions for this task. Include:
- What to build or change
- Which files to look at first
- Any interfaces or signatures to match
- What NOT to do (if there's a real pitfall)

Do not repeat what is in the project context file or sprint context. Task files assume
the worker has already read those.]
```

## Writing Good Tasks

Each task should be executable in a single focused session. If a task is more than a few
hours of work, split it.

**Sprint context** (what every task on this sprint needs to know) goes in the sprint.md body,
not in individual task files.

**Project conventions** (what applies across all sprints) belong in CLAUDE.md.

**Task-specific instructions** (what only this task needs) belong in the task file.

A worker begins a session with no memory of prior sessions. The sprint index + task file +
project context file is everything they have. Make it sufficient.

## After Planning

Tell the human what you produced:
- Number of tasks
- The sprint goal
- Any dependencies worth calling out
- What the human should review before enabling execution

Do not enable the loop or start executing. Planning is a gate the human passes through.
