---
name: research
description: >
  Execute one focused research enquiry. Takes a specific question, searches for answers using
  available tools, produces structured findings. Used as a primitive by the Lisa loop and
  directly by humans for one-off research tasks.
tools:
  - Read
  - Write
  - WebSearch
  - WebFetch
  - Bash
compatibility:
  agents: all
  note: WebSearch and WebFetch availability varies by agent and environment.
---

# /research

Execute a focused research enquiry. Not general-purpose search — a specific question with a
specific output format.

**Usage:**
```
/research "What are the tradeoffs between JWT and session-based auth for a stateless API?"
/research --topic auth --enquiry 003   # part of a Lisa loop run
```

## Output

Write findings to `.loops/research/<topic-slug>/enquiry-NNN.md`:

```yaml
---
id: enquiry-001
topic: auth-strategy
question: "What are the tradeoffs between JWT and session-based auth for a stateless API?"
status: done
sources: []
---

## Findings

[Structured findings. Not a dump — curated. Answer the question directly, then support it.
Include: key facts, specific named sources where they matter, tradeoffs clearly stated,
what remains uncertain.]

## Key Points

- [Specific finding 1]
- [Specific finding 2]
- [What this means for the decision at hand]

## What This Doesn't Answer

[Be honest about gaps. What would you need to know to have higher confidence?]
```

## Research Quality

Answer the question directly. Don't bury the answer in background. The findings should be
usable by a planner or decision-maker reading them without further context.

Distinguish between:
- What you found from sources
- What you inferred
- What you're uncertain about

A shorter, honest findings document is more valuable than a long one with hedged claims.

## After the Enquiry

Report: the question investigated, 2-3 key findings, what gaps remain. If this is part of a
Lisa loop, the runner will handle synthesis and gap evaluation — just write the findings file.
