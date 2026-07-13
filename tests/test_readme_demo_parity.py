"""The README's 60-second section may only quote REAL demo output.

Every ``$ piensalo ...`` command and every quoted output line inside the
README's demo code fences must appear in examples/flagship/TRANSCRIPT.md,
which itself is parity-tested against a fresh run of demo.sh. Truth chain:
README ⊆ TRANSCRIPT == live demo.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_readme_demo_lines_exist_in_transcript():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    transcript = (ROOT / "examples" / "flagship" / "TRANSCRIPT.md").read_text(
        encoding="utf-8")
    tnorm = " ".join(transcript.split())
    section = readme.split("## 60 seconds", 1)[1].split("## Install", 1)[0]
    fences = re.findall(r"```text\n(.*?)```", section, re.S)
    assert fences, "README demo section lost its code fences"
    checked = 0
    for fence in fences:
        lines = fence.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("$ piensalo"):
                cmd = line[2:]
                while cmd.endswith("\\") and i + 1 < len(lines):
                    i += 1
                    cmd = cmd[:-1] + " " + lines[i].strip()
                flat = " ".join(cmd.split())
                assert flat in tnorm, f"README command not in transcript: {flat}"
                checked += 1
            elif line and not line.endswith("\\"):
                assert " ".join(line.split()) in tnorm, \
                    f"README output line not in transcript: {line}"
                checked += 1
            i += 1
    assert checked >= 8, "parity test degenerated (too few lines checked)"
