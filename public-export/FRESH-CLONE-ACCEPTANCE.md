# Fresh-Clone Acceptance — PIÉNSALO identity migration (2026-07-12/13)

Environment: macOS (darwin); system Python 3.9.6 at `python3`; Python 3.11.15
available; Node v25.6.0 / npx 11.8.0; **uv NOT installed** (documented gap);
network available. Clone source: local `$HOME/Desktop/Piensalo` (no public
remote exists). Commit tested: migration HEAD `051af75`.

Exact commands, exact exit codes — no substituted-and-declared-success:

| Command | Exit | Result |
|---|---|---|
| `git clone "$HOME/Desktop/Piensalo" <tmp>/piensalo` | 0 | clean clone, full history |
| `uv sync` | **127** | `uv` not installed on this machine — REQUIRED FLOW ITEM FAILED FOR ENVIRONMENT REASONS; must be re-run on a uv-equipped machine before alpha (ALPHA blocker recorded) |
| `python3 -m pytest -q` | 0 | **49 passed** |
| `python3 evals/harness/grader_selftest.py` | 0 | **ALL GRADER SELF-TESTS PASS** (11 tasks) |
| `make benchmark` | 0 | SMOKE OK: 4 cells graded end-to-end (no API) |
| `piensalo --help` (isolated venv, installed wheel) | 0 | usage renders |
| `piensalo think/inspect/repair/verify/loop/skill --help` | 0 × 6 | all subcommands render |
| `piensalo think examples/math/task.md` | 0 | cognitive program renders |
| `piensalo inspect --task evals/public-tasks/demo-01-discount-stack/task.md --draft examples/math/bare-output.md` | 0 | JSON plan (`no_repair_needed: true` — draft/task mismatch by design of the spot-check) |
| `npx -y skills add . --list` | 0 | lists skill packages, offers `--skill <name>` |

Wheel path (isolated install): built `piensalo-0.1.0.dev0-py3-none-any.whl`
via pip's standard build path (uv absent), inspected (all paths under
`piensalo/`; zero old-package residue), installed into a fresh Python
3.11.15 venv; CLI verified from the venv binary.

NOT verified here (environment or publication gaps, all honest ALPHA items):
- every `uv run ...` form from the directive (uv absent);
- README install lines `uvx piensalo doctor` / `pipx install piensalo` /
  `npx skills add piensalo` — these target the PUBLISHED package, which does
  not exist yet by design (nothing published);
- `examples/basic/` paths from the directive template do not exist in this
  repo layout; the equivalent documented commands above were used.

## Final-HEAD certification mechanism (2026-07-13)
A certification recorded inside a committed file can never equal the commit
it describes (writing it moves HEAD). Certification therefore lives in the
ANNOTATED TAG `piensalo-alpha-ready-candidate`: the acceptance suite runs on
a fresh clone of the exact final commit, and the tag object at that commit
carries the results (`git tag -n99 piensalo-alpha-ready-candidate`). This
supersedes the 051af75 run above; the uv gap is closed (uv 0.11.28).
