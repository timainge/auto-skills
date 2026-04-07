You are continuing the ralph loop. Read the current state and take exactly one action.

## Step 1 — Check whether to continue

Read `.loops/hooks.yaml`. If `ralph.enabled` is `false`, stop normally — the loop has been
paused. Do not execute anything.

Check `.loops/steer.md`. If it exists, read it, incorporate its direction into your decisions
below, then delete it.

## Step 2 — Read current state

Read `.loops/sprint.md`. You need:
- The sprint goal (frontmatter `goal` field)
- The task list (checkboxes)
- The sprint status

For any task that isn't checked off, read its file at `.loops/tasks/<task-id>.md` to check
its `status` field. A task is complete when `status: done` in its file AND its checkbox in
sprint.md is checked. These should agree — if they don't, trust the task file.

## Step 3 — Decide what to do

**If all tasks are done and sprint status is not `done`:**
Run `/evaluate` to assess whether the sprint goal was met. After evaluating, set
`status: done` in sprint.md frontmatter, write a summary, then set `ralph.enabled: false`
in hooks.yaml. Stop.

**If there are failed tasks:**
Set `ralph.enabled: false` in hooks.yaml. Report which tasks failed and why (from their
summary fields). Stop — the human decides whether to retry or replan.

**If there are pending tasks with all dependencies satisfied:**
Find the first such task (respecting the order in sprint.md, and `[depends: ...]` annotations).
Execute it using the `/execute` skill. One task per loop iteration — do not chain multiple tasks.

**If there are pending tasks but all are blocked by incomplete dependencies:**
Something is stuck. Set `ralph.enabled: false`, report the blockage, stop.

## Step 4 — Execute

When executing a task, use the `/execute` skill. The executing agent must not modify:
- `.loops/tasks/<this-task>.md` (it updates status/summary, that's all)
- Any other task file
- `.loops/sprint.md` (it updates the checkbox, that's all)
- `.loops/hooks.yaml`
- `.loops/runner.sh`
- `.loops/prompts/`

## Step 5 — After executing

After execution completes, verify the task file shows `status: done` or `status: failed`.
Update the sprint.md checkbox. Then stop — the hook will fire again and this prompt will
re-run for the next task.

Do not proceed to the next task in the same response. One task per Stop event.
