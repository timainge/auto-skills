#!/usr/bin/env bash
# auto-skills Stop hook dispatcher.
#
# Checks hooks.yaml for enabled loops and injects the corresponding loop prompt.
# Claude reads sprint.md directly and decides what to do — this script is just the trigger.
#
# Returns JSON to stdout:
#   {"decision": "block", "reason": "..."} → Claude continues with injected prompt
#   {"decision": "allow"}                   → Claude stops normally

ROOT="$(cd "$(dirname "$0")" && pwd)"
HOOKS="$ROOT/hooks.yaml"

allow() { echo '{"decision": "allow"}'; exit 0; }

loop_enabled() {
  local loop="$1"
  # Look for the loop block and check if enabled: true follows within it
  awk "/^  $loop:/{found=1} found && /enabled: true/{print; exit} found && /^  [a-z]/{exit}" "$HOOKS" 2>/dev/null | grep -q "enabled: true"
}

inject_prompt() {
  local prompt_file="$ROOT/prompts/$1.md"
  [ -f "$prompt_file" ] || allow
  python3 -c "import json,sys; print(json.dumps({'decision':'block','reason':open(sys.argv[1]).read()}))" "$prompt_file"
  exit 0
}

[ -f "$HOOKS" ] || allow

loop_enabled ralph && inject_prompt ralph
loop_enabled frink && inject_prompt frink
loop_enabled lisa  && inject_prompt lisa

allow
