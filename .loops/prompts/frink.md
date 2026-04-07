You are continuing the frink improvement loop. Read the current state and take exactly one action.

## Step 1 — Check whether to continue

Read `.loops/hooks.yaml`. If `frink.enabled` is `false`, stop normally.

Check `.loops/steer.md`. If it exists, read it, incorporate its direction, then delete it.

Read `.loops/evals/learnings.md` if it exists — this is your accumulated context from prior
iterations. Do not repeat what has already been tried.

## Step 2 — Read current state

Read `.loops/evals/eval.yaml` for the composite score definition and measurement commands.

Check `.loops/evals/iterations/` for prior iteration results. Find the current best baseline
score.

## Step 3 — Run the eval

Run the measurement commands defined in `eval.yaml`. Produce the current composite score.
Compare against the baseline.

## Step 4 — Decide

**If the composite score meets the target threshold defined in eval.yaml:**
Set `frink.enabled: false` in hooks.yaml. Write a final summary to learnings.md. Stop.

**If the last two iterations both showed no improvement (plateau):**
Set `frink.enabled: false` in hooks.yaml. Write what was tried and what's needed to
`decisions-needed.md`. Stop — the human decides the next direction.

**Otherwise:**
Identify the biggest gap between current score and target. Propose one specific change.
Implement it. Re-run the eval. Write the outcome to `.loops/evals/iterations/NNN/`:
- `hypothesis.md` — what you changed and why
- `score-before.json` and `score-after.json`
Append an entry to `learnings.md` — what was tried, whether it helped, why.

## Step 5 — After the iteration

Write the iteration outcome and stop. The hook will fire again for the next iteration.

One hypothesis per iteration. Do not chain multiple changes.
