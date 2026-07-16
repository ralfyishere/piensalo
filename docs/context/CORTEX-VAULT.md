# Cortex Vault — persistent cognitive memory (DESIGNED, future stage)

**Status: DESIGNED. Not implemented. Not a public product.** This document
reserves the architecture and, critically, records the constraints the *current*
gateway work must honor so this layer can be added later **without redesigning
the core**. Nothing here ships in the observe-gateway release.

The Cortex Vault is the long-term memory of the artificial cortex. It lives
**under CONTEXT**, alongside the Context Optimizer and Continuation Capsules —
it is not a fourth public system and gets no separate brand.

```
persistent memory (Vault)
  → task-specific context compilation (Context Optimizer)
    → THINK
      → execute with any model (gateway + adapters)
        → CHECK
          → verified result
            → PROPOSED memory update (never silent, never unverified)
```

The gateway gives PIÉNSALO a nervous system. The Vault gives it long-term
memory. This file makes sure the nervous system is wired so the memory can be
attached later.

---

## 1. The architectural lesson (not the tool)

The pattern — from Karpathy's LLM-friendly wiki approach — that we adopt is the
*shape*, not any Obsidian-specific implementation:

- **immutable raw sources** — never rewritten; the ground truth.
- **a maintained synthesis** — a derived, curated layer that points back to
  sources with exact citations.
- **an inspectable schema + operating instructions** — machine- and
  human-readable conventions (an `AGENTS.md`/schema) so any model or tool can
  read and safely propose changes.

The durable format stays **open and tool-independent**: plain Markdown +
structured JSON, under Git. Obsidian compatibility is *optional*, never
required.

---

## 2. Four layers (map onto existing CONTEXT primitives)

| Layer | Name | What it holds | Existing primitive it extends |
|---|---|---|---|
| **L1** | active working context | the task-specific compiled packet | Context Optimizer `optimized-context.md` |
| **L2** | consolidated cognitive state | active/superseded decisions, constraints, invariants | Continuation Capsule (`context-capsule/1`) |
| **L3** | exact addressable source memory | content-hashed sources, paged on demand | capsule `source_reference` + `sha256` refs |
| **L4** | immutable / version-recoverable archive | historical record, Git history | new; Git-backed |

The capsule schema already carries decision **status**
(`ACTIVE/SUPERSEDED/CONTESTED/TEMPORARY/EXPIRED/UNVERIFIED`), **exactness**
(`EXACT/SEMANTIC/REGENERABLE/DISPOSABLE`), content hashes, and supersession
links. The Vault is largely a *persistence + maintenance* layer over these
existing consequence records — not a new data model.

The Vault must support: plain Markdown + structured JSON · Git/version history ·
source hashes and exact citations · active and superseded decisions · verified /
unverified / contested / stale / expired claims · contradiction detection ·
deduplication · query-miss logging · task-specific compilation · bounded source
expansion · privacy and retention controls · model-independent schema
conventions · optional Obsidian compatibility.

---

## 3. Write discipline (the load-bearing safety rule)

**Never allow an unverified model output to silently become trusted memory.**

Every durable write is a **proposed change**, not an applied one:

1. **Provenance** — which model, which task, which run produced it
   (`requested_model`/`resolved_model`, already recorded).
2. **Validation** — schema-valid and, where possible, CHECK-verified.
3. **Diff** — a reviewable change against current memory (Git diff).
4. **Rollback** — every applied change is version-recoverable.

Claim states are first-class: `verified · unverified · contested · stale ·
expired`. A model output enters as **unverified** at best; only CHECK evidence
can promote it. Contradiction detection flags conflicts with existing ACTIVE
decisions rather than overwriting them.

---

## 4. What the current gateway work must (and must not) do

Honoring the addendum, the observe gateway is built so the Vault can attach
later. Concretely, already true in this branch:

- **Gateway is read-only w.r.t. durable memory.** Observe mode never writes,
  proposes, or promotes memory. It only records an event ledger.
- **Event schema has the seam.** `GatewayEvent` carries `memory_refs_read` and
  `memory_updates_proposed`, both **always empty** in observe mode. They exist
  so a future verified mode can record (a) which memory a request read and (b)
  *proposed* updates — without a schema migration.
- **Request schema is not blocked.** `NormalizedRequest.messages`/`raw` can
  carry an Optimizer-compiled, memory-sourced context packet later; no field
  removal or reshape is needed to add L1 compilation upstream of the model.
- **Provenance is intact.** The adapter contract already records
  requested/resolved model with no silent fallback — exactly the provenance a
  proposed memory write needs.

### Read / write seams (where the Vault plugs in later)

- **READ (L1 compilation):** *before* THINK/execute, the Optimizer would compile
  a task-specific packet from the Vault (L2/L3), logged as `memory_refs_read`.
  This is a read; it is safe in any mode.
- **WRITE (proposed update):** *after* CHECK produces a **verified** result, a
  proposed memory update may be emitted to `memory_updates_proposed` — as a
  diff with provenance, applied only through the review/rollback path in §3,
  and **only in a future verified mode**, never in observe.

---

## 5. Bounded future stage (not now)

This is a later stage, gated behind the gateway's own evidence ladder and
sequenced roughly as:

1. Vault schema + `AGENTS.md` conventions (open Markdown/JSON, Git-backed).
2. L3 exact source store with content hashes + bounded paging.
3. L2 consolidation from Continuation Capsules; contradiction detection + dedup.
4. L1 task-specific compilation via the Context Optimizer; query-miss logging.
5. Proposed-write path (provenance → validation → diff → rollback) wired to a
   verified gateway mode.
6. Optional Obsidian view over the same open files.

Each step earns its own evidence before the next. It does **not** derail the
observe-only gateway; it is recorded here so the core need not be redesigned
when the time comes.
