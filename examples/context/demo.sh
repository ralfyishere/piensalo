#!/bin/sh
# PIENSALO Context demo: compile a real transcript into a verified
# continuation capsule, entirely offline. Regenerates examples/context/generated/.
#
# Compile arguments here are mirrored by tests/test_context_example_parity.py;
# the parity test fails if generated/ and this script drift apart.
set -eu
cd "$(dirname "$0")"

if command -v piensalo >/dev/null 2>&1; then
    PIENSALO="piensalo"
elif command -v uv >/dev/null 2>&1; then
    PIENSALO="uv run piensalo"
else
    PIENSALO="python3 -m piensalo"
fi

echo "== compile (offline, deterministic, model-independent) =="
$PIENSALO context compile transcript.txt \
    --goal "Continue the acme-widgets beta-hardening work in a fresh session" \
    --budget 1200 \
    --project-state project-state.json \
    --output generated

echo
echo "== verify (deterministic structural checks) =="
$PIENSALO context verify generated

echo
echo "== inspect =="
$PIENSALO context inspect generated

echo
echo "== diff (a capsule against itself: no structural changes) =="
$PIENSALO context diff generated generated

echo
echo "Demo complete. resume.md is plain text — paste it into any AI system."
echo "Behavioral equivalence is UNMEASURED: nothing here claims a resumed"
echo "model behaves identically; that verification is future work."
