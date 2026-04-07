# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## What This Project Is

auto-skills implements autonomous development loops — Ralph (plan/execute/evaluate), Frink
(eval-driven improvement), and Lisa (research supervisor) — as portable agent skills and
hooks. The goal is a self-contained plugin any project can adopt by copying a directory.

See `VISION.md` for the full conceptual model. That document is the authoritative design
reference.

## Repository Structure

```
auto-skills/
  VISION.md              ← authoritative design document; read before changing architecture
  README.md              ← user-facing: installation, usage, loop overview
  CLAUDE.md              ← this file

  skills/                ← agentskills.io skill definitions
    plan/SKILL.md        ← /plan: produce sprint.md + task files
    execute/SKILL.md     ← /execute: run one task, update status + summary
    evaluate/SKILL.md    ← /evaluate: check sprint goal against task summaries
    research/SKILL.md    ← /research: one focused enquiry → structured findings

  .loops/                ← runtime directory installed into target projects
    hooks.yaml           ← loop config (enable/disable without touching settings.json)
    runner.sh            ← Stop hook dispatcher: checks enabled loop, injects prompt file
    prompts/
      ralph.md           ← ralph loop continuation prompt (agent reads and acts on this)
      frink.md           ← frink loop continuation prompt
      lisa.md            ← lisa loop continuation prompt
    sprint.md            ← sprint index template
    tasks/               ← task file template
    research/            ← lisa artifacts template
    evals/               ← frink artifacts template
```

## Key Design Principles

**Portability first.** Skills must work via manual invocation in any agentskills.io-compatible
agent. Hooks and sub-agents are enhancements for agents that support them — never required for
core functionality.

**Supervision at the gates.** The human's role is at judgment-heavy transitions: reviewing the
plan before execution, reviewing the evaluation before the next sprint. The loop owns the
structured execution between gates.

**Agent as orchestrator.** The hook is a trigger, not a controller. `runner.sh` only checks
which loop is enabled and injects the corresponding prompt file. The agent reads sprint.md
directly, decides what's next, and takes action. Orchestration logic lives in prompts, not code.

**Lean supervisor session.** When hooks drive the loop, keep the supervisor session lean by
delegating task execution to isolated sub-sessions where the agent supports it. Sub-sessions
write results to task files; the supervisor reads summaries only.

**Loop integrity.** Every execution prompt must include the scope integrity guard (which files
not to modify) backed by a PreToolUse hook that enforces it. The guard exists because the
failure mode is real: an agent will redefine its task to satisfy its completion drive if not
explicitly prevented from doing so.

**File state is always current.** Every state transition writes to disk. The filesystem is a
live, readable snapshot of project state — not an output. Any process can read current state
without asking the running loop.

## Entity Schemas

Task files and sprint.md use the schemas defined in VISION.md. Do not add fields without
updating VISION.md. The schemas are intentionally compatible with autopilot's domain model —
keep them that way.

## Skill Development

Each skill lives in `skills/<name>/SKILL.md` following the agentskills.io spec:
- YAML frontmatter: `name`, `description`, `tools`, `compatibility`
- Instructions under 5000 tokens
- Always include the manual invocation path (no hooks assumed)
- Reference task/sprint schema from VISION.md, don't restate it inline

## Testing

No test suite yet. Validate by:
1. Running the skills manually against a test project
2. Enabling the hook loop in a scratch project
3. Verifying task files update correctly through a full ralph cycle

## Code Style

- `runner.sh` should be readable without context — someone installing this for the first time
  will read it to understand what the Stop hook does. Keep it short.
- No external dependencies anywhere in `.loops/` — stdlib bash + one python3 -c call for JSON
  escaping. The whole point is zero infrastructure.
- Loop logic belongs in `prompts/*.md`, not in `runner.sh`. If you find yourself parsing
  sprint.md in shell, stop — move that decision into the prompt.
