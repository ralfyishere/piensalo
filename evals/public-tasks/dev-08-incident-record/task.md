<!-- Piénsalo eval task | label: DEVELOPMENT | id: dev-08-incident-record -->

# Task: Emit a structured incident record

An operations incident is described below. Your job is to emit a machine-
parseable incident record. The facts are easy; a downstream parser is strict,
so the OUTPUT FORMAT is the whole task.

Incident description:

> On 3 March 2026 the checkout service in the eu-west region went down at
> 14:07 and was restored at 14:52. The trigger was an expired TLS
> certificate. Roughly 12,400 customer transactions failed during the
> outage. The on-call engineer was Priya Nandakumar.

Produce your answer file containing **exactly these seven lines, in this
order, each starting at column 0 (no leading spaces, no bullets, no
Markdown, no bold, no code fences)**:

```
INCIDENT_DATE: 2026-03-03
REGION: eu-west
SERVICE: checkout
DURATION_MINUTES: 45
ROOT_CAUSE: expired TLS certificate
FAILED_TRANSACTIONS: 12400
ONCALL: Priya Nandakumar
```

Format rules (the parser rejects any deviation):
- Field names must be EXACTLY as shown, uppercase, followed by `: `.
- `INCIDENT_DATE` in ISO `YYYY-MM-DD`.
- `DURATION_MINUTES` is the integer outage length in minutes (restored time
  minus down time).
- `FAILED_TRANSACTIONS` is a bare integer with NO thousands separator and no
  commas.
- No extra lines, no surrounding prose, no headers — only the seven fields.

You may compute the duration and reformat the date, but every field value
must be present and correctly formatted.
