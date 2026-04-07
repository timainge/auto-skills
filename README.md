# auto-skills

Autonomous development loops as portable agent skills.

auto-skills gives you `/plan`, `/execute`, `/evaluate`, and `/research` — skills that implement
structured autonomous loops for planning, executing, and improving software projects. Use them
manually in any coding agent, or let them run automatically via Claude Code hooks.

---

## The Loops

**Ralph** — Plan a sprint, execute tasks, evaluate. The basic autonomous outer loop.

**Frink** — Eval-driven improvement without a task list. The agent observes a score, identifies
the biggest gap, makes one change, re-evaluates. Iterates toward a goal.

**Lisa** — Supervised research. The agent answers a question through focused enquiries,
synthesises findings, evaluates coverage, and iterates until satisfied.

---

## How It Works

auto-skills uses three things: skills (the capabilities), a sprint index with task files (the
state), and optionally hooks (the automation).

```
.loops/
  hooks.yaml        ← enable/disable loops; toggle without touching settings.json
  runner.sh         ← Stop hook: checks enabled loop, injects prompt. That's all.
  prompts/
    ralph.md        ← loop continuation instructions Claude reads and acts on
    frink.md
    lisa.md
  sprint.md         ← sprint index: ordered tasks, dependencies, sprint goal
  tasks/
    task-001.md     ← individual task: instructions, done criteria, summary
    task-002.md
```

The hook is a trigger, not a controller. `runner.sh` injects the loop prompt; Claude reads
`sprint.md` directly, determines what's next, and acts. Orchestration logic lives in prompts.

### Manual (any agent)

```
/plan "add authentication"     → writes sprint.md + task files
# review and adjust task files
/execute task-001              → runs task, updates status + summary
/execute task-002
/evaluate                      → GOAL_MET or NEEDS_WORK
```

### Automated (Claude Code)

```
/plan "add authentication"     → writes sprint.md + task files
# review and adjust task files
# set ralph.enabled: true in .loops/hooks.yaml
# Claude Code now drives the loop autonomously via Stop hook
```

---

## Portability

Skills follow the [agentskills.io](https://agentskills.io) spec and work in any compatible
agent: Claude Code, Cursor, Windsurf, GitHub Copilot, Gemini CLI, and others.

Hooks and sub-agents are Claude Code enhancements. The manual invocation path always works
without them.

---

## Installation

Copy `.loops/` and `.claude/skills/` into your project. For Claude Code hook automation, add
the Stop hook to `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [{ "command": "python .loops/runner.py" }]
  }
}
```

---

## Design

See [VISION.md](VISION.md) for the full conceptual model: the entity hierarchy, loop
mechanics, supervision model, session topology, and loop integrity patterns.
