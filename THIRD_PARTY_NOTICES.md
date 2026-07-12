# Third-Party Notices

Fable Think aims for a minimal dependency surface: the core is designed to run
offline from the Python standard library wherever practical.

## Runtime dependencies

None required for the core at 0.1.0-dev. Optional model adapters may use the
respective provider SDKs or plain HTTP; installing an adapter's extras is an
explicit, opt-in step (`pip install "piensalo[<adapter>]"`), and each
extra's license is listed here when it is added.

| Component | Dependency | License | Notes |
|---|---|---|---|
| core | (none) | — | stdlib only |
| adapters (optional extras) | to be listed per adapter at first release | — | opt-in only |

## Development dependencies

Development and CI use `pytest` (MIT) and standard Python build tooling
(`build`, `setuptools` — MIT/PSF-adjacent licenses). These are not shipped to
users.

## Names and trademarks

- "Claude" and "Anthropic" are trademarks of Anthropic, PBC. Fable Think is an
  independent open-source project. It is not affiliated with or endorsed by
  Anthropic.
- "OpenAI" is a trademark of OpenAI. "Ollama" and "Obsidian" are trademarks of
  their respective owners. References in this repository describe
  interoperability only and imply no affiliation or endorsement.

## Reporting

If a dependency appears in the released package without a corresponding entry
here, that is a bug — please open an issue.
