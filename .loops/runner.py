#!/usr/bin/env python3
"""
auto-skills Stop hook runner.

Reads hooks.yaml to determine which loop is active, finds the next action,
and returns a block decision to drive the loop forward.

Called by Claude Code after every assistant response:
  settings.json: { "hooks": { "Stop": [{ "command": "python .loops/runner.py" }] } }

Returns JSON to stdout:
  {"decision": "block", "reason": "<prompt>"}   → Claude continues with injected prompt
  {"decision": "allow"}                           → Claude stops normally
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
HOOKS_YAML = ROOT / "hooks.yaml"
SPRINT_FILE = ROOT / "sprint.md"
TASKS_DIR = ROOT / "tasks"
STATE_FILE = ROOT / ".state.json"


# ---------------------------------------------------------------------------
# YAML frontmatter parser (stdlib only — no PyYAML dependency)
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter from a markdown file. Returns {} if none."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm_text = text[3:end].strip()
    result = {}
    for line in fm_text.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def parse_hooks_yaml() -> dict:
    """Parse hooks.yaml. Returns defaults if file missing."""
    if not HOOKS_YAML.exists():
        return {"loops": {}}
    text = HOOKS_YAML.read_text()
    # Minimal parser — enough to read enabled flags and simple fields
    loops: dict = {}
    current_loop = None
    current_section = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        if stripped == "loops:":
            current_section = "loops"
            continue
        if current_section == "loops":
            indent = len(line) - len(line.lstrip())
            if indent == 2 and stripped.endswith(":"):
                current_loop = stripped[:-1]
                loops[current_loop] = {}
            elif indent == 4 and current_loop and ":" in stripped:
                key, _, val = stripped.partition(":")
                val = val.strip()
                if val.lower() == "true":
                    val = True
                elif val.lower() == "false":
                    val = False
                elif val.isdigit():
                    val = int(val)
                loops[current_loop][key.strip()] = val
    return {"loops": loops}


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"session_count": 0, "last_task": None}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ---------------------------------------------------------------------------
# Sprint / Task helpers
# ---------------------------------------------------------------------------

def parse_sprint() -> tuple[dict, list[dict]]:
    """Returns (sprint_frontmatter, tasks).

    tasks is a list of dicts with keys: id, title, status, depends.
    """
    if not SPRINT_FILE.exists():
        return {}, []

    text = SPRINT_FILE.read_text()
    fm = parse_frontmatter(text)

    tasks = []
    for line in text.splitlines():
        m = re.match(r"\s*-\s+\[([ x])\]\s+(task-\d+):\s+(.+)", line)
        if m:
            done = m.group(1) == "x"
            task_id = m.group(2)
            rest = m.group(3)

            depends: list[str] = []
            dep_m = re.search(r"\[depends:\s*([^\]]+)\]", rest)
            if dep_m:
                depends = [d.strip() for d in dep_m.group(1).split(",")]
                title = rest[: dep_m.start()].strip()
            else:
                title = rest.strip()

            tasks.append({
                "id": task_id,
                "title": title,
                "done": done,
                "depends": depends,
            })

    return fm, tasks


def get_task_status(task_id: str) -> str:
    task_file = TASKS_DIR / f"{task_id}.md"
    if not task_file.exists():
        return "pending"
    fm = parse_frontmatter(task_file.read_text())
    return fm.get("status", "pending")


def next_unblocked_task(tasks: list[dict]) -> dict | None:
    """Find the first pending task whose dependencies are all done."""
    done_ids = {t["id"] for t in tasks if get_task_status(t["id"]) in ("done",)}
    for task in tasks:
        if get_task_status(task["id"]) != "pending":
            continue
        if all(dep in done_ids for dep in task["depends"]):
            return task
    return None


def build_execute_prompt(task_id: str, sprint_fm: dict) -> str:
    task_file = TASKS_DIR / f"{task_id}.md"
    task_text = task_file.read_text() if task_file.exists() else f"Task file not found: {task_id}"
    goal = sprint_fm.get("goal", "(no sprint goal set)")

    return f"""You are running inside the ralph loop. Your job is to execute one task.

Sprint goal: {goal}

Task to execute: {task_id}

---
{task_text}
---

Use the /execute skill to execute this task. Spawn a sub-agent for isolation.

The sub-agent MUST NOT modify:
- .loops/tasks/{task_id}.md
- Any other file in .loops/tasks/
- .loops/sprint.md
- .loops/hooks.yaml
- .loops/runner.py

When execution is complete, update {task_id}.md (status + summary) and mark the task
checkbox done in .loops/sprint.md.

After completing this task, stop. Do not proceed to the next task — the loop will handle that."""


def build_evaluate_prompt(sprint_fm: dict) -> str:
    goal = sprint_fm.get("goal", "(no sprint goal set)")
    return f"""All tasks in the sprint are complete.

Sprint goal: {goal}

Use the /evaluate skill to evaluate the sprint. Read all task summaries from .loops/tasks/,
check them against the sprint goal, and produce a GOAL_MET or NEEDS_WORK verdict.

After evaluating, write the verdict summary into .loops/sprint.md frontmatter and set
status: done. Then report the verdict to the human and stop."""


# ---------------------------------------------------------------------------
# Loop handlers
# ---------------------------------------------------------------------------

def handle_ralph(config: dict, state: dict) -> dict:
    max_sessions = config.get("max_sessions", 20)

    if state["session_count"] >= max_sessions:
        return allow(f"Ralph loop: max_sessions ({max_sessions}) reached. Stopping.")

    sprint_fm, tasks = parse_sprint()
    if not tasks:
        return allow("Ralph loop: no tasks found in sprint.md.")

    # Check if all tasks are done
    all_done = all(get_task_status(t["id"]) in ("done", "failed") for t in tasks)
    if all_done:
        sprint_status = sprint_fm.get("status", "")
        if sprint_status == "done":
            return allow("Ralph loop: sprint complete and evaluated.")
        return block(build_evaluate_prompt(sprint_fm))

    next_task = next_unblocked_task(tasks)
    if next_task is None:
        return allow("Ralph loop: no unblocked pending tasks. Manual intervention needed.")

    state["session_count"] += 1
    state["last_task"] = next_task["id"]
    save_state(state)

    return block(build_execute_prompt(next_task["id"], sprint_fm))


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def block(reason: str) -> dict:
    return {"decision": "block", "reason": reason}


def allow(message: str | None = None) -> dict:
    if message:
        print(message, file=sys.stderr)
    return {"decision": "allow"}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    hooks = parse_hooks_yaml()
    loops = hooks.get("loops", {})
    state = load_state()

    ralph_cfg = loops.get("ralph", {})
    if ralph_cfg.get("enabled"):
        result = handle_ralph(ralph_cfg, state)
        print(json.dumps(result))
        return

    # Frink and Lisa loops: not yet implemented
    frink_cfg = loops.get("frink", {})
    if frink_cfg.get("enabled"):
        print(json.dumps(allow("Frink loop: not yet implemented.")))
        return

    lisa_cfg = loops.get("lisa", {})
    if lisa_cfg.get("enabled"):
        print(json.dumps(allow("Lisa loop: not yet implemented.")))
        return

    print(json.dumps(allow()))


if __name__ == "__main__":
    main()
