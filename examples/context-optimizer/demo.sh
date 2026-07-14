#!/bin/sh
# PIENSALO Context Optimizer demo.
#
# Step 1 is deterministic and offline (anti-drift tested byte-for-byte).
# Step 2 calls a real model through the explicitly configured claude-cli
# adapter and is therefore NOT byte-reproducible; the committed
# generated/evaluation/ is one real recorded run, produced by this script.
#
# Optimize arguments are mirrored by tests/test_optimizer_example_parity.py.
set -eu
cd "$(dirname "$0")"

if command -v piensalo >/dev/null 2>&1; then PIENSALO="piensalo";
elif command -v uv >/dev/null 2>&1; then PIENSALO="uv run piensalo";
else PIENSALO="python3 -m piensalo"; fi

echo "== 1. optimize (deterministic, offline, model-independent) =="
$PIENSALO context optimize \
    --task task.md \
    --context context.txt \
    --budget 1500 \
    --output generated/optimize

echo
echo "== 2. paired full-vs-optimized evaluation (real model call) =="
if command -v claude >/dev/null 2>&1; then
    $PIENSALO context evaluate \
        --task task.md \
        --context context.txt \
        --adapter claude-cli \
        --model claude-haiku-4-5-20251001 \
        --contract contract.json \
        --expected expected.json \
        --budgets 1500 \
        --output generated/evaluation
else
    echo "claude CLI not found — skipping the model-backed comparison."
    echo "The committed generated/evaluation/ is a real recorded run."
fi
