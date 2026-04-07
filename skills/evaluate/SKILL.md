---
name: evaluate
description: >
  Evaluate a completed sprint against its goal. Reads task summaries, checks done criteria,
  produces GOAL_MET or NEEDS_WORK with specific gaps. Human reviews before next sprint begins.
tools:
  - Read
  - Bash
compatibility:
  agents: all
---

# /evaluate

Evaluate the current sprint. Reads `.loops/sprint.md` and all task summaries, checks against
the sprint goal, produces a verdict.

**Usage:**
```
/evaluate
/evaluate sprint-001
```

## What to Read

1. `.loops/sprint.md` — sprint goal, eval field (if set), and task list
2. Each task file — done_criteria and summary
3. If `eval` in sprint frontmatter contains a shell command, run it

## Verdict Format

Produce one of two verdicts:

**GOAL_MET**
```
## Evaluation: GOAL_MET

Sprint goal: [restate the goal]

All tasks completed. Key outcomes:
- [what was built or changed]
- [any decisions made during execution worth noting]
- [anything that differed from the plan and why]

Eval: [if shell eval ran, report its output]
```

**NEEDS_WORK**
```
## Evaluation: NEEDS_WORK

Sprint goal: [restate the goal]

Gaps:
- [specific gap: what is missing or not working]
- [another gap]

Failed tasks: [list any tasks with status: failed and their error]

Suggested next steps:
- [specific action to address each gap]
```

## After Evaluating

Write the verdict and your summary into `sprint.md`:
- Set `status: done` (even if NEEDS_WORK — the sprint ran; a new sprint addresses gaps)
- Write a one-paragraph `summary` into the frontmatter

Then report the verdict to the human. Do not start a new sprint or replan automatically.
The human decides what happens next.

## Note on Eval Quality

Avoid generic verdicts. "The feature is implemented" is not a useful summary. "JWT middleware
validates tokens on all protected routes; unauthenticated requests return 401; existing tests
pass; login endpoint returns tokens in the expected format" is useful.

Read the done_criteria for each task and verify each one specifically. If you can't verify a
criterion from the task summaries alone, say so — the human may need to test manually.
