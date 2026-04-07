# auto-skills

Autonomous development loops as portable agent skills.

Plan a sprint, execute tasks, evaluate — driven by Claude reading your project files directly.
Use the skills manually in any coding agent, or enable the hook loop in Claude Code for fully
autonomous execution.

---

## Install

Copy `.loops/` into your project root and add the skills to your agent.

**Claude Code:** add the Stop hook to `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [{ "command": "bash .loops/runner.sh" }]
  }
}
```

---

## Usage

### 1. Plan a sprint

```
/plan "add JWT authentication"
```

Produces `.loops/sprint.md` (the task index) and individual files in `.loops/tasks/`. Review
and adjust them — this is the human's contribution before execution begins.

```
.loops/
  sprint.md          ← ordered task list, sprint goal, dependencies
  tasks/
    task-001.md      ← instructions + done criteria for each task
    task-002.md
    task-003.md
```

### 2a. Execute manually (any agent)

Run tasks one at a time:

```
/execute task-001
/execute task-002
/execute task-003
/evaluate
```

Each `/execute` runs the task via a sub-agent, then writes the outcome back to the task file.
`/evaluate` checks all task summaries against the sprint goal and returns `GOAL_MET` or
`NEEDS_WORK`.

### 2b. Execute automatically (Claude Code)

Enable the ralph loop in `.loops/hooks.yaml`:

```yaml
loops:
  ralph:
    enabled: true
```

Claude Code's Stop hook now drives the loop. After each response, `runner.sh` injects the
ralph prompt; Claude reads `sprint.md`, finds the next unblocked task, executes it via
sub-agent, updates state, and stops. The hook fires again for the next task.

**Pause anytime** — set `ralph.enabled: false`. The loop stops at the next Stop event.

**Steer mid-loop** — drop a `.loops/steer.md` file. Claude reads it at the next iteration,
acts on it, and deletes it. No session restart needed.

### 3. Research (Lisa loop)

Run a supervised research enquiry:

```
/research "what are the tradeoffs between JWT and session-based auth?"
```

Or run the iterative Lisa loop for deeper investigation:

```yaml
# .loops/hooks.yaml
loops:
  lisa:
    enabled: true
    topic: auth-strategy
```

Lisa plans enquiries, executes them, synthesises findings, evaluates coverage, and iterates
until the question is answered. Output lands in `.loops/research/auth-strategy/`:

```
plan.md          ← enquiry plan
enquiry-001.md   ← findings per enquiry
enquiry-002.md
report.md        ← synthesised findings (rewritten each iteration)
gaps.md          ← what remains unanswered
summary.md       ← 3-5 sentence summary for use as planning context
```

Steer mid-loop: drop `.loops/research/auth-strategy/steer.md`.

### 4. Improve (Frink loop)

Define a composite eval score in `.loops/evals/eval.yaml`, then enable Frink:

```yaml
loops:
  frink:
    enabled: true
```

Frink runs the eval, identifies the biggest gap, makes one targeted change, re-evaluates.
Iterates until the target score is met or it plateaus. Outcomes and learnings accumulate in
`.loops/evals/`.

---

## Supervision

The human owns the judgment gates. The loop owns the structured execution between them.

| Gate | Human action |
|------|-------------|
| Before execution | Review task files, adjust scope, enable loop |
| Mid-loop pause | `ralph.enabled: false` in hooks.yaml |
| Mid-loop steer | Drop `steer.md` — read and deleted at next iteration |
| After sprint | Review `/evaluate` output, decide on next sprint |

---

## Portability

Skills follow the [agentskills.io](https://agentskills.io) spec. The manual invocation path
(`/plan` → `/execute` → `/evaluate`) works in any compatible agent: Claude Code, Cursor,
Windsurf, GitHub Copilot, Gemini CLI, and others.

Hook automation and sub-agent isolation are Claude Code enhancements layered on top.

---

## Design

See [VISION.md](VISION.md) for the full conceptual model: entity hierarchy, loop mechanics,
session topology, loop integrity patterns, and portability layers.
