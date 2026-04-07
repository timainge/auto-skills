---
name: execute
description: >
  Execute a single task from the sprint. Spawns a sub-agent for isolation, updates task
  status and summary on completion. The loop runner calls this automatically; humans can
  also invoke it directly.
tools:
  - Read
  - Write
  - Edit
  - Agent
compatibility:
  agents: all
  note: >
    Sub-agent spawning requires agent support (e.g. an Agent tool or equivalent). In agents
    without this capability, execute inline. The loop runner calls this automatically in
    hook-capable agents; invoke manually in others.
---

# /execute

Execute a single task. Takes a task file path as argument, or defaults to the next pending
task in `.loops/sprint.md`.

**Usage:**
```
/execute task-001
/execute .loops/tasks/task-001.md
/execute                          # next pending unblocked task from sprint.md
```

## Execution Model

By default, spawn a sub-agent to execute the task. This keeps the supervisor session lean —
the sub-agent works in isolation; its output lands in the task file; the supervisor reads the
summary only.

```
1. Read .loops/tasks/task-NNN.md
2. Verify dependencies are done (check sprint.md)
3. Spawn sub-agent with:
   - Task file contents
   - Project context file (e.g. CLAUDE.md or equivalent) if present
   - Sprint context from sprint.md body (if present)
   - The scope integrity guard (below)
4. Sub-agent executes, writes work to project files
5. Sub-agent updates task file: status → done, summary → one paragraph
6. Update sprint.md: mark task checkbox done
```

If `isolation: false` in the task frontmatter, execute inline instead of spawning a sub-agent.

## Scope Integrity Guard

Include this in every sub-agent prompt. Do not shorten or omit it:

```
You are executing [task-NNN.md]. You must not modify:
- .loops/tasks/task-NNN.md (the task file that defines your work)
- Any other task file in .loops/tasks/
- .loops/sprint.md
- .loops/hooks.yaml
- .loops/runner.sh

Your work goes to the project files described in the task instructions.

When done:
1. Open .loops/tasks/task-NNN.md
2. Set status: done (or failed if you could not complete it)
3. Write a summary: one paragraph describing what was done, any decisions made,
   and anything the next task should know. If failed, describe what was tried and why
   it didn't work.
4. Do not continue working after writing the summary. Stop.
```

## On Completion

After the sub-agent finishes:
1. Read the task file — verify status is `done` or `failed`
2. Update the sprint.md checkbox for this task
3. Report to the human: task name, status, one-sentence summary

If the task failed:
- Increment `attempts` in the task frontmatter
- Do not automatically retry — report the failure to the human
- The human decides whether to retry, replan, or skip

## After Executing

Tell the human: which task ran, whether it succeeded or failed, and the one-sentence summary.
If there are more pending tasks, tell the human what's next but do not start it automatically
(unless running inside the loop).
