# auto-skills

Autonomous development loops as portable agent skills.

Plan a sprint, execute tasks, evaluate — driven by your agent reading your project files
directly. Use the skills manually in any coding agent, or enable the hook loop in agents that
support stop-event hooks for fully autonomous execution.

---

## What

auto-skills gives you three loops:

- **Ralph** — plan → execute → evaluate. Takes a goal, breaks it into tasks, runs them, checks
  the outcome. The human reviews the plan before execution starts and the evaluation before the
  next sprint.

- **Lisa** — research supervisor. Decomposes a question into enquiries, runs them in parallel,
  synthesises findings, identifies gaps, iterates until the question is answered.

- **Frink** — eval-driven improvement. Runs a composite eval, identifies the biggest gap, makes
  one targeted change, re-evaluates. Iterates until the target score is met or it plateaus.

## Why

Coding agents work well on focused tasks but drift on multi-step goals without structure. These
loops provide that structure without locking you into a specific agent or platform. The skills
are portable: the manual invocation path works in any compatible agent. Hook automation is
layered on top for agents that support it.

## How

Install by copying `.loops/` into your project root and adding the skills to your agent.

Skills follow the [agentskills.io](https://agentskills.io) spec. The manual invocation path
(`/plan` → `/execute` → `/evaluate`) works in any compatible agent: Claude Code, Cursor,
Windsurf, GitHub Copilot, Codex, OpenHands, and others.

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

### 2b. Execute automatically (hook-capable agents)

Enable the ralph loop in `.loops/hooks.yaml`:

```yaml
loops:
  ralph:
    enabled: true
```

The stop hook now drives the loop. After each response, `runner.sh` injects the ralph prompt;
your agent reads `sprint.md`, finds the next unblocked task, executes it, updates state, and
stops. The hook fires again for the next task.

**Pause anytime** — set `ralph.enabled: false`. The loop stops at the next stop event.

**Steer mid-loop** — drop a `.loops/steer.md` file. Your agent reads it at the next iteration,
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

## Agent Setup

Hook configuration is agent-specific. See the wiki for setup guides:

- [Claude Code](../../wiki/Claude-Code)
- [GitHub Copilot](../../wiki/GitHub-Copilot)
- [OpenAI Codex](../../wiki/OpenAI-Codex)

---

## Design

See [VISION.md](VISION.md) for the full conceptual model: entity hierarchy, loop mechanics,
session topology, loop integrity patterns, and portability layers.
