You are continuing the lisa research loop. Read the current state and take exactly one action.

## Step 1 — Check whether to continue

Read `.loops/hooks.yaml`. Get the `lisa.topic` slug. If `lisa.enabled` is `false`, stop.

Check `.loops/research/<topic-slug>/steer.md`. If it exists, read it, incorporate its
direction into your decisions below, then delete it.

## Step 2 — Read current state

In `.loops/research/<topic-slug>/`:
- `plan.md` — the enquiry plan (questions to investigate). May not exist yet on first iteration.
- `enquiry-NNN.md` files — completed enquiries so far
- `report.md` — synthesised findings so far (if exists)
- `gaps.md` — identified gaps from last synthesis (if exists)

## Step 3 — Decide what to do

**No plan exists yet (first iteration):**
Read the topic from hooks.yaml. Write `plan.md`: decompose the topic into 3-5 focused
enquiries, each a specific answerable question. Order them — broader context-setting first,
then specifics. Then execute the first enquiry using `/research`.

**Plan exists, enquiries remain:**
Find the next planned enquiry that hasn't been executed yet. Execute it using `/research`.
Write findings to `enquiry-NNN.md`.

**All planned enquiries done:**
Synthesise all enquiry findings into `report.md`. Then evaluate coverage: does the report
sufficiently answer the original topic? Write your assessment to `gaps.md`.

If gaps are significant: plan new enquiries to address them, append to `plan.md`, execute
the first new enquiry.

If the topic is sufficiently answered (or max_iterations reached): write `summary.md` — a
3-5 sentence summary suitable for use as planning context. Set `lisa.enabled: false` in
hooks.yaml. Stop.

## Step 4 — After the action

Write outputs and stop. The hook will fire again for the next enquiry or synthesis step.

One action per iteration: either one enquiry or one synthesis pass. Do not chain both.
