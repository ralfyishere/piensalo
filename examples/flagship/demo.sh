#!/usr/bin/env bash
# PIÉNSALO flagship demo — deterministic, offline, no model calls.
# Invoke from the repo root (the script cd's there itself, so any cwd works):
#   examples/flagship/demo.sh
#
# What it shows, in order:
#   1. inspect the broken draft  -> a repair is selected from observable evidence
#   2. repair (offline default)  -> an honestly-labeled packet; nothing is applied
#   3. verify the broken draft   -> the wrong total lands under FAILED
#   4. inspect the correct draft -> NO REPAIR NEEDED (abstention is a success)
#   5. verify the correct draft  -> CONTRACT VERIFIED + DETERMINISTICALLY VERIFIED
#
# Exit codes are printed rather than hidden: verify on the broken draft is
# EXPECTED to exit 1 — that is the tool telling the truth.
set -u
cd "$(dirname "$0")/../.."
PY="${PYTHON:-python3}"
F=examples/flagship

run() {
  echo "\$ piensalo $*"
  PYTHONPATH=src "$PY" -m piensalo "$@"
  echo "[exit: $?]"
  echo
}

run inspect --task "$F/task.md" --draft "$F/draft-broken.md" --contract "$F/contract.json"
run repair --task "$F/task.md" --draft "$F/draft-broken.md" --contract "$F/contract.json"
run verify --task "$F/task.md" --draft "$F/draft-broken.md" --contract "$F/contract.json"
run inspect --task "$F/task.md" --draft "$F/draft-correct.md" --contract "$F/contract.json"
run verify --task "$F/task.md" --draft "$F/draft-correct.md" --contract "$F/contract.json"
