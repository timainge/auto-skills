# auto-skills Vision

_Autonomous development loops as portable agent skills._

---

## What This Is

auto-skills implements a set of conceptual patterns — autonomous planning, execution, research,
and improvement loops — using agent skills and hooks as the substrate. The loops are the same
ones you'd find in a full orchestration framework; the infrastructure is minimal.

Skills are portable across any agent that supports the agentskills.io spec. Hooks provide
automation for agents that support event-driven hooks. You can run the loops manually in any
coding agent, or let them run autonomously in agents with hook support.

---

## The Conceptual Model

### Entity Hierarchy

```
Roadmap: Sprint[]   ← goal + phases; optional
Sprint:  Task[]     ← coherent unit of work; optional
Task:    atomic     ← always valid alone
```

This is a composition model, not a dependency model. A Task is valid on its own. A Sprint is
valid without a Roadmap. The hierarchy describes how entities relate when composed — it does not
impose existence requirements on lower-level entities.

**A Roadmap** expresses a goal with phases and a defined completion condition.
**A Sprint** is a coherent unit of work with a shared goal. Tasks in a sprint share context.
**A Task** is the smallest executable unit: a specific intent, done criteria, and a summary
written on completion.

The same interface applies at every level:
- **Intent** — what is to be done
- **Lifecycle state** — pending → active → done / failed
- **Eval** — optional formal definition of done
- **Completion summary** — written on completion (success or failure); feeds planner context cheaply

### Why Completion Summaries Matter

A planner reading the history of a project should not have to read full task transcripts.
Completion summaries — a paragraph written by the executing agent into the task's `summary`
field — give the planner exactly what it needs: what was done and what was learned, compressed
to fit in a planning context without noise.

Failure summaries are as valuable as success summaries. "We tried X and it failed because Y"
is exactly the context the next planner needs.

### Eval as a First-Class Concept

An eval is the formal definition of done. Any entity can have one:

- **Task** → a shell assertion, an expected output, a specific functional check
- **Sprint** → integration review, test suite
- **Roadmap** → goal completion signal, quantitative metric, LLM judge

```yaml
eval:
  - type: shell
    run: "pytest tests/"
  - type: judge
    prompt: "does this feature work end to end for a real user?"
  - type: metric
    run: "python measure.py"
    threshold: 0.95
```

---

## The Loops

### Ralph Loop — Plan → Execute → Evaluate

The basic outer loop. A human plans a sprint (writes task files with intent and done criteria),
reviews and approves, then the loop executes tasks sequentially. At the end, an evaluate step
checks whether the sprint goal was met.

The supervision boundary is explicit: humans own the planning and approval gates. The loop owns
the structured execution phase.

```
human:  /plan  →  sprint.md (index) + task files
human:  review →  adjust scope, context, order
human:  approve → enable execution
loop:   /execute × N → each task, one per iteration
loop:   /evaluate  → GOAL_MET or NEEDS_WORK
human:  review     → accept or replan
```

### Frink Loop — Eval-Driven Improvement

An improvement loop without pre-planned tasks. The agent observes an eval signal, identifies
the biggest gap, makes one targeted change, re-evaluates. Each iteration moves toward a goal
defined by the eval, not by a pre-written task list.

The eval is not a check at the end — it is the steering mechanism.

```
human:  define eval  →  eval.yaml (composite score + measurement commands)
loop:   run eval     →  identify biggest gap
loop:   hypothesise  →  propose one change, record hypothesis
loop:   implement    →  make the change
loop:   re-evaluate  →  compare scores
        if improved: advance baseline, continue
        if plateau×2: pause, write decisions-needed.md
```

Each iteration writes to `.loops/evals/iterations/NNN/` — what changed, before/after scores,
and an outcome entry in `learnings.md`. Learnings persist across sessions and seed future
iterations.

### Lisa Loop — Research → Synthesise → Gap Eval → Iterate

A supervised research loop. The agent works through focused enquiries to answer a question,
synthesises findings, evaluates coverage, and continues until the question is sufficiently
answered or the human is satisfied.

```
human:  set topic    →  hooks.yaml or /research <question>
loop:   plan enquiries → 3-5 focused questions to investigate
loop:   execute enquiries → each produces structured findings
loop:   synthesise   →  report.md from all findings so far
loop:   gap eval     →  what remains unanswered?
        if gaps: plan new enquiries, continue
        if satisfied: write summary.md, stop
```

The `steer.md` pattern: drop a file at `.loops/research/<slug>/steer.md` at any point. The
runner injects its contents into the next iteration prompt, then deletes it. Mid-flight
direction without stopping the session or breaking the loop.

---

## Supervision Model

Every loop has a human-readable, human-editable state on the filesystem. At any point you can:
- Read what's been done (task summaries, sprint index)
- Read what's in progress (active task, current research report)
- Pause the loop (set `enabled: false` in hooks.yaml)
- Redirect mid-loop (drop `steer.md`)
- Resume from exactly where it stopped (file state is always current)

The supervision boundary is at the judgment-heavy transitions:
- **Plan gate**: human reviews the sprint before execution begins
- **Evaluate gate**: human reviews the sprint verdict before the next sprint begins
- **Steer point**: human can inject direction at any iteration without stopping

Autonomous execution lives between the gates. The gates are where human judgment matters most.

---

## The Agent as Orchestrator

The hook is a trigger, not a controller. When the stop event fires, a minimal shell script
checks whether a loop is enabled in hooks.yaml and, if so, injects a loop prompt. That's it.
The agent reads sprint.md directly, determines what's next, executes it, and updates state.

The orchestration intelligence lives in the prompt files (`.loops/prompts/ralph.md` etc.),
not in code. An agent is better at reading structured files and making decisions than a parser
is — so that's where the logic belongs.

```
stop event fires
  → runner.sh checks hooks.yaml
    → if ralph enabled: inject .loops/prompts/ralph.md
      → agent reads sprint.md, finds next unblocked task
        → delegates task execution (sub-agent or inline)
          → execution writes results to task file
            → agent updates sprint.md checkbox
              → stop event fires again → repeat
```

The runner has no knowledge of task structure, dependency resolution, or loop state. It only
needs to know: which loop is enabled, and where its prompt lives.

---

## Session Topology

In hook-driven loops, context accumulates across tasks in the same Claude session. This is the
fundamental difference from a framework that spawns a fresh session per task.

**Advantage**: coherent work — later tasks see what earlier tasks found. Useful for design work
where the plan evolves as execution proceeds.

**Liability**: long sprints are expensive. Each response sees the full prior context.

**Mitigation**: where the agent supports sub-agent spawning, delegate each task to an isolated
sub-session. The supervisor session only sees the task summary, not the full execution
transcript. The supervisor stays lean regardless of task complexity.

```
supervisor session (lean, persistent across sprint)
  └── sub-agent per task (isolated, discarded after completion)
        └── writes: task status + summary to task file
              └── supervisor reads: summary only
```

This maps to the same isolation pattern that a full orchestration framework achieves via
external process spawning — without the external process.

---

## Loop Integrity

Autonomous agents in a loop have a structural failure mode: they can redefine the scope of
their own work to satisfy their completion drive. This is not a malfunction — it's optimisation
in the wrong direction.

A real incident: an agent in a similar hook-driven system rewrote its design spec into an
implementation spec — because implementing felt like a more complete form of done — and then
kept working because its task said "produce a design doc" and it now had an implementation spec
that didn't match. Internally coherent. Catastrophic for the loop.

Two-layer protection:

**Prompt layer** (reasoning): every execution prompt explicitly tells the agent which files it
must not modify and why. This gives the agent the reason — which helps it make better decisions
at boundaries the enforcement layer doesn't cover.

**Enforcement layer** (structural): a PreToolUse hook inspects every Write/Edit call before
it executes and blocks writes to protected paths. The agent physically cannot modify its task
definition file, the sprint index, or the runner infrastructure.

Prompt reasoning + structural enforcement. Both layers together.

---

## File Layout

```
project/
  .loops/
    hooks.yaml          ← loop config; toggle on/off without touching settings.json
    runner.sh           ← Stop hook dispatcher: checks enabled loop, injects prompt
    prompts/
      ralph.md          ← loop continuation instructions (agent reads + acts on these)
      frink.md
      lisa.md
    sprint.md           ← sprint index + metadata
    tasks/
      task-NNN.md       ← individual task: instructions + status + summary
    steer.md            ← drop-in steering for ralph/frink (agent reads + deletes)
    research/
      <topic-slug>/
        plan.md
        enquiry-NNN.md
        report.md
        gaps.md
        summary.md
        steer.md        ← drop-in steering for lisa (agent reads + deletes)
    evals/
      eval.yaml
      iterations/
        NNN/
          hypothesis.md
          score-before.json
          score-after.json
      learnings.md
```

---

## Entity Schemas

### Task

```yaml
---
id: task-001
title: "Add authentication middleware"
status: pending        # pending | active | done | failed
depends: []
done_criteria:
  - Middleware validates JWT tokens on every protected route
  - Unauthenticated requests return 401
  - Existing tests still pass
summary: ""            # written by the executing agent on completion
attempts: 0
isolation: true        # execute via sub-agent (default); false = inline
---

## Instructions

[Task body written by /plan. Specific intent, relevant file paths and interfaces,
any constraints. Does not repeat what is in the project context file or sprint context.]
```

### Sprint Index

```yaml
---
id: sprint-001
title: "Authentication"
status: active         # pending | active | done | failed
goal: "Users can log in with email/password; JWT tokens are validated on protected routes"
approved: false
eval: ""               # optional: shell command or judge prompt
summary: ""            # written by /evaluate on completion
---

## Tasks

- [ ] task-001: Create user model and migration
- [ ] task-002: Implement JWT generation [depends: task-001]
- [ ] task-003: Add middleware validation [depends: task-002]
- [ ] task-004: Write integration tests [depends: task-003]
```

---

## Portability Layers

```
Layer 1 — Skills only
  Works in any agent supporting the agentskills.io spec.
  Manual invocation: /plan → review → /execute → review → /evaluate
  No automation. Human drives each step.

Layer 2 — Skills + Hooks
  Agents with hook/stop-event support.
  Stop hook drives ralph/frink/lisa loops automatically.
  Human sets enabled: true in hooks.yaml; loop runs until paused or done.

Layer 3 — Skills + Hooks + Sub-agents
  Agents with both hook support and sub-agent spawning.
  Execution delegated to isolated sub-sessions per task.
  Supervisor session stays lean. Parallelism for independent tasks.
```

Skills always include the manual invocation path. Hooks and sub-agents are additive.
Any agent gets the skills. Agents with hook support get the full loop.
