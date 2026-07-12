# Key — dev-08-incident-record

The facts are trivially extractable; the task is the exact output contract.
Correct answer file is EXACTLY these seven lines and nothing else:

```
INCIDENT_DATE: 2026-03-03
REGION: eu-west
SERVICE: checkout
DURATION_MINUTES: 45
ROOT_CAUSE: expired TLS certificate
FAILED_TRANSACTIONS: 12400
ONCALL: Priya Nandakumar
```

Derivations: 14:52 - 14:07 = 45 minutes; "3 March 2026" -> ISO 2026-03-03;
"12,400" -> bare integer 12400 (no comma).

Contract violations that a correct-but-casual answer commits (each fails the
delivery/rendering layer while cognition passes):
- Wrapping fields in bold (`**INCIDENT_DATE**: ...`) or a ```code fence```.
- Writing `FAILED_TRANSACTIONS: 12,400` with a thousands separator.
- Adding a preamble ("Here is the incident record:") or a trailing note.
- Renaming fields (`DATE`, `TRANSACTIONS_FAILED`) or lowercasing names.
- Reordering or indenting the lines (not at column 0).

Cognition passes iff all seven facts are present in any recognizable form;
contract passes iff the seven exact lines are the entire answer.
