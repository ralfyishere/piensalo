# Claim-to-Code Ledger

Every material public claim, classified against the shipping code at the
commit this file ships in. Statuses: **TRUE AS SHIPPED** · **TRUE WITH
QUALIFICATION** · (nothing currently ASPIRATIONAL or BROKEN — such claims
were removed or fixed in the v0.1.0-alpha.2 truthfulness pass).

| Claim (surface) | Status | Basis |
|---|---|---|
| README hero: model-independent cognitive OS for understanding/inspection/repair/verification/abstention/continuation | TRUE AS SHIPPED | shipped CLI modes think/inspect/repair/verify/loop/skill; adapters for 4 interfaces; abstention path tested |
| 60-second demo transcript | TRUE AS SHIPPED | committed capture of `examples/flagship/demo.sh`; CI parity tests re-run the demo and diff it (`test_flagship_transcript.py`), and README quotes are asserted ⊆ transcript (`test_readme_demo_parity.py`) |
| `uvx --from git+…` install | TRUE AS SHIPPED | executed against the live repo (exit 0) |
| `git clone` + `uv sync` install | TRUE AS SHIPPED | fresh-clone CI + local certification |
| `uvx piensalo` / `pipx install piensalo` (PyPI) | TRUE WITH QUALIFICATION | PyPI publication rides the v0.1.0-alpha.2 release via trusted publishing; verified immediately post-release. pipx form additionally unverifiable on the build machine (local pipx bootstrap broken) — standard behavior assumed |
| `npx skills add ralfyishere/piensalo` | TRUE AS SHIPPED | `npx -y skills add . --list` verified from clone; remote-slug form verified post-publication of alpha.1 |
| `think` accepts file OR inline text | TRUE AS SHIPPED | deterministic resolution + `--file`/`--text` overrides, tested incl. paths with spaces |
| `repair` offline mode "instructions, nothing applied" | TRUE AS SHIPPED | packet is labeled exactly so; test asserts the label |
| `repair --adapter` writes new file + provenance + re-inspects | TRUE AS SHIPPED | never overwrites source; sidecar with requested/resolved model; re-inspection printed; tested with fixture adapter |
| `verify` five-bucket truth report; UNMEASURED ≠ pass | TRUE AS SHIPPED | bucket rendering tested; cognition without an oracle always lands in UNMEASURED with the explicit not-a-pass line |
| Numerical verification | TRUE WITH QUALIFICATION | deterministic only where the contract supplies an expected value; generic semantic correctness is explicitly NOT determined |
| `loop` bounded, resumable, model-attributed | TRUE AS SHIPPED | session lifecycle, prompt gate, provenance, stop conditions; unit-tested (no live long-run publicly demonstrated yet) |
| Offline core, zero telemetry, no network without explicit adapter | TRUE AS SHIPPED | zero runtime deps; adapters lazy + explicit; `doctor` never touches network |
| Silent model fallback prohibited | TRUE AS SHIPPED | adapters raise `ModelFallbackError` on mismatch; claude-cli asserts `modelUsage` |
| Model support table (4 interfaces) | TRUE WITH QUALIFICATION | interfaces implemented + unit-tested; live validation exists for the Claude family only — stated wherever the table appears |
| Evidence claims (+18.8pp, 30% delivery reduction, harm law, etc.) | TRUE WITH QUALIFICATION | two pre-registered 120-cell runs, n=8 tasks each, one execution model family; confounds attached in BENCHMARKS.md; nothing PROMOTED |
| "Every capability ships with receipts" | TRUE AS SHIPPED | EVIDENCE.md mechanism records incl. NARROW/REJECTED; NEGATIVE-RESULTS.md public |
| Security: skill scan, no shell from untrusted skill text | TRUE AS SHIPPED | `skill scan` shipped + tested; threat model documents residual risk |
| CI badge/green | TRUE AS SHIPPED (as of alpha.2) | Skill lint root-caused (`__main__.py` + multi-path lint); parity + link + secret + build + smoke jobs |
| Python 3.10–3.13, Linux+macOS | TRUE AS SHIPPED | CI matrix runs exactly these; Windows explicitly unsupported |

Removed in this pass (were ASPIRATIONAL or stale): handwritten README
transcript with nonexistent syntax (`--strategy`, inline `loop --continue`,
positional inspect); "private alpha"/"after publication"/"not published"
language; "alpha gate passed" roadmap line (replaced by the truthful
five-line hierarchy).
