"""FROZEN task set for the cortex-value evaluation (see PREREGISTRATION.md).

12 tasks. Each defines: full input (task_text + optional context_text/draft),
budgets, expected router decision (human eligibility judgment), critical
requirements, forbidden outcomes, and a grader key into graders.py.

Frozen at preregistration commit time. Do not edit after results exist.
"""

TASKS = [
    # ---------------------------------------------------------------- simple
    {
        "id": "01-simple-arith",
        "category": "simple",
        "task_text": "What is 17 * 23? Reply with only the number.",
        "context_text": None,
        "expected_router": "PASS_THROUGH",
        "cortex_eligible": False,
        "context_budget": None,
        "critical": ["answer is exactly 391"],
        "forbidden": ["any answer other than 391"],
        "grader": "arith",
    },
    {
        "id": "02-simple-haiku",
        "category": "simple-creative (scaffolding-harm probe)",
        "task_text": (
            "Write a haiku about the sea. Output exactly three lines and "
            "nothing else — no title, no preamble, no explanation."
        ),
        "context_text": None,
        "expected_router": "PASS_THROUGH",
        "cortex_eligible": False,
        "context_budget": None,
        "critical": ["exactly three non-empty lines", "no preamble/meta text"],
        "forbidden": ["extra prose around the poem"],
        "grader": "haiku",
    },
    # -------------------------------------------------------------- planning
    {
        "id": "03-plan-schedule",
        "category": "difficult-planning",
        "task_text": (
            "Plan the schedule for five jobs on two workers and derive the "
            "minimum makespan.\n\n"
            "Jobs and durations (hours): A=2, B=1, C=3, D=2, E=4.\n"
            "Dependencies: C may start only after A finishes. D may start "
            "only after B finishes.\n"
            "Each worker runs one job at a time; jobs are not splittable; "
            "both workers start at hour 0.\n\n"
            "Output exactly one line per job and then the final line, in this "
            "format and nothing else:\n"
            "A: worker=<1|2> start=<hour> end=<hour>\n"
            "B: worker=<1|2> start=<hour> end=<hour>\n"
            "C: worker=<1|2> start=<hour> end=<hour>\n"
            "D: worker=<1|2> start=<hour> end=<hour>\n"
            "E: worker=<1|2> start=<hour> end=<hour>\n"
            "MAKESPAN: <hours>"
        ),
        "context_text": None,
        "expected_router": "THINK",
        "cortex_eligible": True,
        "context_budget": None,
        "critical": [
            "all five jobs scheduled with correct durations",
            "no dependency violated",
            "no worker overlap",
            "stated MAKESPAN equals the schedule's real makespan",
        ],
        "forbidden": ["invalid schedule presented as valid"],
        "requirements": ["makespan equals the optimum (6)"],
        "grader": "schedule",
    },
    {
        "id": "04-plan-migration",
        "category": "difficult-planning",
        "task_text": (
            "Plan the execution order of a database migration with six steps: "
            "B (backup), R (rollback plan), S (schema change), D (data "
            "migration), V (verification), C (cutover).\n\n"
            "Constraints:\n"
            "1. B must be the very first step.\n"
            "2. R must come immediately after B, before any change is made.\n"
            "3. S must come before D.\n"
            "4. D must come before V.\n"
            "5. V must come before C.\n"
            "6. C must be the very last step.\n\n"
            "Exactly one order satisfies all constraints. Output only one "
            "line, exactly in this format:\n"
            "ORDER: <letter>,<letter>,<letter>,<letter>,<letter>,<letter>"
        ),
        "context_text": None,
        "expected_router": "THINK",
        "cortex_eligible": True,
        "context_budget": None,
        "critical": ["order is exactly B,R,S,D,V,C"],
        "forbidden": ["an order violating a stated constraint"],
        "grader": "order",
    },
    # ---------------------------------------------------- long-context tasks
    {
        "id": "05-longctx-release",
        "category": "long-context-distractor",
        "task_text": (
            "Using the meeting transcript provided as context, state the "
            "FINAL agreed values (the last decision made for each, not "
            "earlier proposals). Output exactly these four lines and nothing "
            "else:\n"
            "SERVICE: <name>\nPORT: <number>\nVERSION: <x.y.z>\nDATE: <YYYY-MM-DD>"
        ),
        "context_text": (
            "Sprint sync, Tuesday. Attendees: Mara, Jonas, Priya, Ted.\n\n"
            "Mara opened with the marketing update. The newsletter went out to "
            "eighteen thousand subscribers and click-through was up two points. "
            "Someone asked about the conference booth; Ted said the banner "
            "artwork is stuck with the vendor. Long tangent about whether the "
            "booth needs a demo station or just tablets. No decision.\n\n"
            "Jonas moved to the release. The gateway service was provisionally "
            "called 'bifrost' in the spring planning doc, and the old wiki "
            "still says 'bifrost' in three places. Priya reminded everyone the "
            "trademark search killed that name in May. The replacement "
            "shortlist was 'atlas' and 'meridian'. After the legal check came "
            "back clean on both, the team voted and settled on atlas. Final: "
            "the service ships under the name atlas. Someone should fix the "
            "wiki.\n\n"
            "Ports. The prototype ran on 8080 like everything always does. "
            "Security review said no unencrypted listener, so the January plan "
            "moved it to 8443. Then the platform team pointed out 8443 "
            "collides with the ingress controller on shared staging, so the "
            "final allocation from the port registry is 9443. Jonas repeated "
            "it twice because people keep writing 8443 in tickets: the "
            "production listener is 9443.\n\n"
            "Ted gave a long status on the loyalty-points batch job, which is "
            "unrelated to the release but ran long overnight. It reprocessed "
            "four hundred thousand rows. Priya suggested moving it to the new "
            "queue. Parked for next sprint.\n\n"
            "Versioning. The release branch was cut as 2.3.9 back when it was "
            "a patch. Scope grew: the auth rewrite landed, so semver says "
            "minor bump, and the doc draft briefly said 2.4.0. A regression "
            "fix merged after the branch cut forced one more increment. The "
            "version that will actually be tagged is 2.4.1. Mara asked if "
            "that's what goes in the press note; Jonas confirmed: 2.4.1.\n\n"
            "Dates. The original target was 2026-08-30, which slipped when the "
            "auth rewrite grew. The next proposal was 2026-09-08, but that "
            "week collides with the platform freeze. The team committed to "
            "2026-09-15 as the ship date and Priya put it on the shared "
            "calendar. Ted joked that the only real date is 'when the tests "
            "pass'. The calendar says 2026-09-15.\n\n"
            "Closing: Mara wants the blog draft by Friday. Jonas owes the "
            "runbook update. Meeting ended eleven minutes over.\n\n"
            "Addendum, Wednesday standup notes (same thread). Hiring: two "
            "backend candidates moved to onsite; the sourcing pipeline for "
            "the SRE role is thin and the recruiter wants referrals by "
            "Friday. Support rotation: the new escalation macro cut median "
            "first-response time to nine minutes; Ted wants that number in "
            "the quarterly deck. A customer anecdote from the enterprise "
            "onboarding call ran long — their old integration still points "
            "at the deprecated 8080 sandbox from the 2024 pilot, and they "
            "asked whether that would keep working. Answer: the sandbox is "
            "unrelated to this release and will be retired separately; "
            "nothing about the production listener changes for them until "
            "cutover day.\n\n"
            "Thursday follow-up thread. The load-test report for the new "
            "ingress path came back: p99 held under two hundred "
            "milliseconds at twice projected launch traffic, with one "
            "retransmit anomaly on the synthetic burst test that the "
            "platform team attributes to the lab switch, not the service. "
            "Someone asked again in the thread whether the listener was "
            "8443 — Jonas replied with a pin emoji and repeated the "
            "registry allocation: 9443 in production, full stop. The docs "
            "team confirmed the API reference regenerates from the openapi "
            "file, so the port constant only needs fixing in one place. "
            "Two more housekeeping notes: the changelog template now pulls "
            "the version from the release tag automatically, so nobody "
            "should hand-edit version strings into the docs again — the "
            "2.4.0 draft note was exactly that kind of hand-edit and it is "
            "obsolete; and the status-page maintenance window still shows "
            "the abandoned September 8 draft date, which comms will replace "
            "with the committed calendar date this week."
        ),
        "expected_router": "CONTEXT",
        "cortex_eligible": True,
        "context_budget": 700,
        "critical": [
            "SERVICE is atlas", "PORT is 9443", "VERSION is 2.4.1",
            "DATE is 2026-09-15",
        ],
        "forbidden": ["a superseded value (bifrost, 8080, 8443, 2.3.9, 2.4.0, "
                       "2026-08-30, 2026-09-08) reported as final"],
        "grader": "release_values",
        "contract_fields": ["SERVICE", "PORT", "VERSION", "DATE"],
    },
    {
        "id": "06-longctx-decisions",
        "category": "long-context-distractor",
        "task_text": (
            "Using the engineering notes provided as context, state the FINAL "
            "standing decision for each item (later decisions supersede "
            "earlier ones). Output exactly these three lines and nothing "
            "else:\n"
            "DB: <name>\nRETENTION: <days>\nREGION: <region-code>"
        ),
        "context_text": (
            "Engineering decision log, raw notes, June-July.\n\n"
            "June 3. Storage working group. The analytics service needs its "
            "own store. MongoDB came up first because the events are "
            "schemaless-ish; Dev advocated hard for it and the June 3 note "
            "records 'leaning mongo'. Karim wanted benchmarks before "
            "committing. Side discussion about the office plants dying — "
            "facilities ticket filed.\n\n"
            "June 10. Benchmarks done on synthetic load. Mongo fine at p50, "
            "ugly at p99 under the join-heavy dashboard queries. Postgres with "
            "jsonb handled both. Karim: 'we already run postgres everywhere "
            "else, ops knows it.' Decision recorded June 10: the analytics "
            "store is postgres. Dev conceded after seeing the p99 chart. This "
            "decision was re-confirmed in the July 1 review — postgres, "
            "final.\n\n"
            "June 12. Long thread about retention. Legal's default template "
            "says 90 days for event data. That's what the first draft policy "
            "said. Finance flagged storage cost projections at 90 days as "
            "over budget by a third. Compromise proposal on June 20: 60 days. "
            "Then the privacy review landed July 2 and pushed the other "
            "direction — minimize by default. Final policy signed July 8: "
            "retention is 30 days for raw events. The 90-day number still "
            "appears in the old template; ignore it, the signed policy says "
            "30.\n\n"
            "June 18. Interlude: the deploy-bot renamed itself 'captain-hook' "
            "after the webhook migration. Everyone kept the name. Not a "
            "decision anyone will admit to.\n\n"
            "June 25. Region. The prototype ran in us-east-1 because that's "
            "the default in the terraform module. GDPR assessment says the "
            "analytics data includes EU subject events, so the data must live "
            "in the EU. Options were eu-central-1 and eu-west-1. Network "
            "latency from the ingest fleet favored eu-west-1 by 9ms. July 5 "
            "infra meeting locked it: production region eu-west-1. The "
            "us-east-1 prototype stays up for one more sprint, then dies.\n\n"
            "July 9. Follow-ups: dashboard rewrite scheduled; Karim on "
            "call-rotation cleanup; someone water the plants.\n\n"
            "July 11. On-call retro, appended to the same log because nobody "
            "opens a second doc in July. Three pages last week: one flapping "
            "disk alert on the legacy metrics box (silenced, box dies next "
            "month), one genuine OOM in the report renderer traced to an "
            "unbounded template loop (fix merged), one false alarm from the "
            "synthetic checker hitting the us-east-1 prototype after its DNS "
            "record was half-removed — a reminder that the prototype is "
            "still up on borrowed time and confuses tooling; it is not, and "
            "will not be, the production region. Action item: fence the "
            "checker to production endpoints only.\n\n"
            "July 15. Cost review. The storage line for analytics came in "
            "under the revised projection, which finance attributes to the "
            "shorter retention window that the signed policy set — the old "
            "90-day figure in the unsigned draft template keeps getting "
            "quoted in slide decks and Karim has now stapled a correction "
            "to the template header. Compute costs are flat. The Grafana "
            "license renewal moved to the platform budget. One more decoy "
            "for future readers: a vendor pitch deck this week proposed "
            "hosting a 'turnkey analytics stack' in their us-east-1 cloud; "
            "it was declined without a meeting, and it changes nothing "
            "about where the production data lives.\n\n"
            "July 16. Misc: the dashboard rewrite kickoff slipped two days; "
            "captain-hook got a profile picture; Dev is writing the postgres "
            "index-tuning runbook for the new store, which everyone agrees "
            "is the most Dev sentence ever recorded."
        ),
        "expected_router": "CONTEXT",
        "cortex_eligible": True,
        "context_budget": 700,
        "critical": ["DB is postgres", "RETENTION is 30", "REGION is eu-west-1"],
        "forbidden": ["a superseded value (mongo, 90, 60, us-east-1, "
                       "eu-central-1) reported as final"],
        "grader": "decision_values",
        "contract_fields": ["DB", "RETENTION", "REGION"],
    },
    # ------------------------------------------------------- exact / struct
    {
        "id": "07-exact-json",
        "category": "structured-output",
        "task_text": (
            "Product facts: The 'Northwind Kettle' costs 49 US dollars and 90 "
            "cents, it is currently in stock, and its catalog tags are "
            "kitchen, steel, and 1.7-liter.\n\n"
            "Produce a JSON object for this product. Requirements:\n"
            "1. Keys must be exactly: name, price_usd, in_stock, tags.\n"
            "2. price_usd must be a number (not a string).\n"
            "3. in_stock must be a boolean.\n"
            "4. tags must be an array of exactly 3 strings.\n"
            "5. Output only the JSON object — no code fences, no prose.\n"
        ),
        "context_text": None,
        "expected_router": "CHECK",
        "cortex_eligible": True,
        "context_budget": None,
        "critical": [
            "output parses as JSON with exactly the four keys",
            "price_usd == 49.9 (number)", "in_stock == true (boolean)",
            "tags == the 3 stated strings",
            "no prose or fences around the JSON",
        ],
        "forbidden": ["invalid JSON", "extra keys", "stringified numbers"],
        "grader": "product_json",
    },
    {
        "id": "08-exact-fields",
        "category": "exact-constraints",
        "task_text": (
            "Incident: At 03:12 UTC the payment service began rejecting 100% "
            "of card transactions due to an expired TLS certificate on the "
            "processor callback endpoint. Revenue impact is total while it "
            "lasts. The fix (certificate rotation) is known, tested, and "
            "takes about ten minutes to apply.\n\n"
            "Write the incident triage block. Output exactly these four "
            "lines in exactly this format, nothing else:\n"
            "SUMMARY: <one sentence, at most 25 words>\n"
            "RISK: <exactly one of LOW|MEDIUM|HIGH>\n"
            "ACTION: <imperative phrase, at most 12 words>\n"
            "CONFIDENCE: <integer 0-100>"
        ),
        "context_text": None,
        "expected_router": "CHECK",
        "cortex_eligible": True,
        "context_budget": None,
        "critical": [
            "all four anchored lines present, in order, no extra lines",
            "RISK is HIGH", "CONFIDENCE is an integer 0-100",
        ],
        "forbidden": ["RISK LOW or MEDIUM for a total-payment-outage",
                       "extra prose lines"],
        "grader": "triage_fields",
        "contract_fields": ["SUMMARY", "RISK", "ACTION", "CONFIDENCE"],
    },
    # ---------------------------------------------------------- code / tool
    {
        "id": "09-code-function",
        "category": "coding",
        "task_text": (
            "Write a Python function `parse_duration(s)` that converts a "
            "duration string into total minutes.\n\n"
            "Requirements:\n"
            "1. '2h30m' -> 150, '45m' -> 45, '1h' -> 60, '90m' -> 90, "
            "'0m' -> 0.\n"
            "2. Hours component is optional; minutes component is optional; "
            "at least one is present.\n"
            "3. Raise ValueError for an empty string or malformed input like "
            "'abc' or '2x30m'.\n"
            "4. Output only the function definition in a single ```python "
            "code block, no usage examples, no prose.\n"
        ),
        "context_text": None,
        "expected_router": "CHECK",
        "cortex_eligible": True,
        "context_budget": None,
        "critical": [
            "all five value cases return the exact expected integers",
            "ValueError raised on '', 'abc', '2x30m'",
            "exactly one python code block, function only",
        ],
        "forbidden": ["wrong arithmetic", "missing error handling"],
        "grader": "duration_code",
    },
    {
        "id": "10-tool-use",
        "category": "tool-use",
        "task_text": (
            "Fetch the current weather for Madrid. You must call the "
            "get_weather tool to do this — do not answer from memory and do "
            "not describe the tool; call it."
        ),
        "context_text": None,
        "expected_router": "PASS_THROUGH",
        "cortex_eligible": False,
        "context_budget": None,
        "tools": ["get_weather", "get_time"],
        "critical": ["exactly one tool call", "tool is get_weather",
                      "arguments name the city Madrid"],
        "forbidden": ["answering from memory instead of calling the tool",
                       "calling the wrong tool"],
        "grader": "tool_call",
    },
    # -------------------------------------------------- abstention / unsafe
    {
        "id": "11-already-correct",
        "category": "already-correct (CHECK must abstain)",
        "task_text": (
            "Review the draft triage block below. If it fully satisfies the "
            "required format, deliver it unchanged; only change it if a "
            "requirement is violated.\n\n"
            "Required format, exactly four lines:\n"
            "STATUS: <exactly one of APPROVED|REJECTED>\n"
            "OWNER: <team name>\n"
            "DEADLINE: <YYYY-MM-DD>\n"
            "TICKET: <ABC-#### id>"
        ),
        "draft_text": (
            "STATUS: APPROVED\n"
            "OWNER: platform-security\n"
            "DEADLINE: 2026-08-01\n"
            "TICKET: SEC-4211"
        ),
        "context_text": None,
        "expected_router": "CHECK",
        "cortex_eligible": True,
        "context_budget": None,
        "critical": [
            "final output contains the four lines with the exact original "
            "values", "no rewriting of a compliant draft"],
        "forbidden": ["changed values", "added prose", "dropped lines"],
        "grader": "draft_preserved",
        "contract_fields": ["STATUS", "OWNER", "DEADLINE", "TICKET"],
    },
    {
        "id": "12-unsafe-budget",
        "category": "unsafe-optimization (must refuse + safe fallback)",
        "task_text": (
            "Using the frozen interface specification provided as context, "
            "answer: what is the exact value of parameter X7, and what is the "
            "required checksum format? Output exactly these two lines and "
            "nothing else:\n"
            "X7: <value>\nCHECKSUM: <format>"
        ),
        # Marker-format context: every CONSTRAINT/INVARIANT is ACTIVE and
        # therefore mandatory to the optimizer. Total mandatory size is far
        # above the frozen 120-token budget, so optimization MUST refuse and
        # the runtime MUST fall back to full context.
        "context_text": (
            "OBJECTIVE: Implement the v3 ingestion endpoint exactly per the "
            "frozen interface specification below; every constraint is "
            "load-bearing and none may be dropped.\n"
            "CONSTRAINT: Parameter X1 (batch size) is fixed at 250 records "
            "per request; requests with more records are rejected with error "
            "code E-4001.\n"
            "CONSTRAINT: Parameter X2 (flush interval) is 500 milliseconds; "
            "the client must not buffer longer under any load condition.\n"
            "CONSTRAINT: Parameter X3 (retry ceiling) is 4 attempts with "
            "exponential backoff starting at 200 milliseconds.\n"
            "CONSTRAINT: Parameter X4 (payload encoding) is UTF-8 JSON; "
            "gzip is applied only when the body exceeds 32 kilobytes.\n"
            "CONSTRAINT: Parameter X5 (auth header) is 'X-Ingest-Key' and "
            "rotates every 24 hours via the key-management endpoint.\n"
            "CONSTRAINT: Parameter X6 (idempotency window) is 15 minutes; "
            "duplicate keys inside the window return the original response.\n"
            "CONSTRAINT: Parameter X7 (max in-flight requests) is 512; the "
            "server sheds load with error E-4290 beyond that.\n"
            "CONSTRAINT: The checksum of every batch is computed as crc32 "
            "and transmitted as lowercase hexadecimal in the 'X-Batch-CRC' "
            "header; the required checksum format is crc32-hex.\n"
            "INVARIANT: Field ordering inside a record is not significant; "
            "consumers must not depend on it.\n"
            "INVARIANT: The endpoint never returns partial-success; a batch "
            "is atomic — all records land or none do.\n"
            "CONSTRAINT: Parameter X8 (clock skew tolerance) is 30 seconds; "
            "timestamps outside the window are rejected with error E-4008 "
            "and must not be silently clamped by the client.\n"
            "CONSTRAINT: Parameter X9 (dead-letter policy) routes batches "
            "that fail all retry attempts to the 'ingest-dlq' topic with "
            "the original headers preserved verbatim.\n"
            "CONSTRAINT: Parameter X10 (schema version header) is "
            "'X-Schema-Rev' and must equal the value served by the schema "
            "registry at send time; stale revisions are rejected with "
            "error E-4090.\n"
            "CONSTRAINT: Parameter X11 (rate limit) is 40 requests per "
            "second per key, enforced with a token bucket of burst size 80; "
            "clients must honor the Retry-After header on E-4290.\n"
            "CONSTRAINT: Parameter X12 (record size cap) is 64 kilobytes "
            "per record before compression; oversized records fail the "
            "whole batch under the atomicity invariant.\n"
            "CONSTRAINT: Parameter X13 (TLS floor) is TLS 1.3; connections "
            "offering lower versions are refused at the listener, not "
            "downgraded.\n"
            "INVARIANT: Error codes in the E-4xxx range are stable API "
            "surface; clients may branch on them and the numbering never "
            "changes within a major version.\n"
            "INVARIANT: The specification above is frozen for v3; any "
            "deviation requires a major-version bump, not a client-side "
            "workaround.\n"
        ),
        "expected_router": "CONTEXT",
        "cortex_eligible": True,
        "context_budget": 120,
        "critical": ["X7 is 512", "CHECKSUM is crc32-hex",
                      "cortex arm: optimizer refused and fell back safely "
                      "(never silently truncated)"],
        "forbidden": ["an answer produced from silently truncated context"],
        "grader": "spec_values",
        "contract_fields": ["X7", "CHECKSUM"],
        "fallback": "run",
    },
]

TOOL_DEFS = {
    "get_weather": {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city",
            "parameters": {"type": "object",
                           "properties": {"city": {"type": "string"}},
                           "required": ["city"]},
        },
    },
    "get_time": {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get the current local time for a city",
            "parameters": {"type": "object",
                           "properties": {"city": {"type": "string"}},
                           "required": ["city"]},
        },
    },
}


def by_id(task_id: str) -> dict:
    for t in TASKS:
        if t["id"] == task_id:
            return t
    raise KeyError(task_id)
