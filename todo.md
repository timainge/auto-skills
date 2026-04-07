# Todo

## Now — make it runnable

- [ ] Fix `runner.sh`: the `loop_enabled` awk check is fragile — test it against the actual
      hooks.yaml format and fix before first real use
- [ ] Add `chmod +x .loops/runner.sh` to install instructions (or handle in the hook command)
- [ ] Test ralph loop end-to-end against a real scratch project — verify Stop hook fires,
      prompt injects, Claude reads sprint.md correctly, task file updates, loop terminates
- [ ] Fix README install section: settings.json currently references `runner.py` (old name) —
      already updated but double-check after test
- [ ] Validate skill frontmatter against agentskills.io spec — confirm `tools`, `compatibility`
      field names are correct
- [ ] Add `.claude/settings.json` template to the repo so install is copy-paste

## Soon — skill quality

- [ ] `/plan` skill: write a worked example showing good vs bad task files — the quality of
      task files is the quality of the loop; the skill needs to set a high bar
- [ ] `/execute` skill: clarify what "spawn a sub-agent" means in practice — the Agent tool
      invocation, what context to pass, how to verify the sub-agent completed correctly
- [ ] `/evaluate` skill: add guidance on what NEEDS_WORK output should contain — specific
      enough that the human knows exactly what to replan, not just "gaps exist"
- [ ] All skills: test manual invocation path in Claude Code without hook — confirm each
      skill works as a standalone command

## Soon — loop prompt quality

- [ ] ralph.md: test the dependency resolution instructions — does Claude reliably find the
      correct next unblocked task from sprint.md format?
- [ ] ralph.md: test the loop termination — does Claude correctly set `ralph.enabled: false`
      and stop after evaluate?
- [ ] steer.md: test the inject-and-delete pattern — confirm Claude deletes it reliably
- [ ] lisa.md: the `<topic-slug>` interpolation is a gap — the prompt references it but
      Claude has to derive it from hooks.yaml; make this explicit
- [ ] frink.md: needs a worked example of `eval.yaml` format before it's usable

## Later — Frink and Lisa loops

- [ ] Define `eval.yaml` schema and document it in VISION.md
- [ ] Frink: implement the learnings.md accumulation pattern — seed from prior sessions
- [ ] Frink: add `decisions-needed.md` output for escalation cases
- [ ] Lisa: implement the gap eval pattern — how does Claude assess "sufficiently answered"?
      needs a rubric or structured assessment format to avoid over-confident coverage claims
- [ ] Lisa: parallel enquiries — can Claude execute multiple enquiries in one iteration via
      parallel Agent calls? worth testing

## Later — project structure

- [ ] Consider whether `.loops/` should be `.claude/loops/` or live elsewhere — placement
      affects discoverability and gitignore conventions
- [ ] Add a `PreToolUse` hook to enforce the scope integrity guard structurally (not just
      via prompt) — block writes to `.loops/tasks/`, `sprint.md`, `hooks.yaml` during execution
- [ ] Installation: write a `/setup` skill or shell script that copies `.loops/` into a
      target project and patches settings.json
- [ ] Publish to agentskills.io registry once skills are validated
