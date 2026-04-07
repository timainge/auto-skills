# Research Todo

Researching automation/hook equivalents for each major coding agent.
Output in `.dev/research/`.

| Agent | Slug | Status |
|-------|------|--------|
| Claude Code | `claude-code-automation` | complete |
| GitHub Copilot | `copilot-automation` | complete |
| OpenAI Codex | `codex-automation` | complete |

## Goal

Find the equivalent of Claude Code's Stop hook for each agent — any mechanism that lets
auto-skills' `runner.sh` (or equivalent) fire after each agent response to drive the
ralph/lisa/frink loops automatically.

## Findings Summary

| Agent | Stop hook equivalent | Notes |
|-------|---------------------|-------|
| Claude Code | Yes — `Stop` in `settings.json` | 26 total hook events; 4 handler types |
| GitHub Copilot | Yes — `Stop` in `.github/hooks/*.json` | VS Code agent mode only; cloud agent does not support |
| OpenAI Codex | Yes — `Stop` in `.codex/hooks.json` | v0.114+; requires `codex_hooks = true` feature flag |

All three hook-capable agents check `stop_hook_active` on stdin — must exit 0 when true to
prevent infinite loops. The `runner.sh` pattern is directly portable to Codex and Copilot.

## Reports

- `.dev/research/claude-code-automation/report.md`
- `.dev/research/copilot-automation/report.md`
- `.dev/research/codex-automation/report.md`
