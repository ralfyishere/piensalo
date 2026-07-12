<!-- Piénsalo eval task | label: DEVELOPMENT | id: dev-02-log-error-filter -->

# Task: List services that logged an error

The file `public-context/events.log` contains one event per line, each with a
timestamp, a level (`INFO`/`WARN`/`ERROR`/`DEBUG`), a service name, and a
message.

Apply this constraint: consider **only lines at level `ERROR`**. For each such
line, take its **service name**. List those service names **in the order the
error lines appear** in the file, one per line.

Deliverable contract for your answer file:

- A line exactly `ERROR_SERVICES:` on its own.
- Then the service names, one per line, in order of appearance, each starting
  at column 0.

Nothing else is required.
