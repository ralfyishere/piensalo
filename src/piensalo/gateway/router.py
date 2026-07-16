"""The Cortex Router — one inspectable, deterministic policy layer.

The router maps a :class:`NormalizedRequest` to exactly one decision and always
explains why. It is intentionally *not* a learned classifier: every reason is a
string a human can audit, and the same request always yields the same decision.

In ``observe`` mode the decision is **shadow only**: it is recorded in the event
ledger and reported by ``gateway inspect``, but it never changes the request or
the response. Acting on a decision is a later-stage capability, gated on
evidence.

Discipline: ``PASS_THROUGH`` is the default and a *successful* outcome. The
router must not recommend intervention merely because it is available. Thresholds
come from configuration so operators can inspect and override them.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from .protocol import NormalizedRequest

# The full decision vocabulary (brief §7). Observe mode records these; it acts
# on none of them.
DECISIONS = (
    "PASS_THROUGH",
    "THINK",
    "CONTEXT",
    "CHECK",
    "THINK_AND_CONTEXT",
    "CONTEXT_AND_CHECK",
    "FULL_CORTEX",
    "ABSTAIN",
    "FALLBACK",
)

# Deterministic signal patterns. These are heuristics for *what the cortex would
# consider*, not guarantees. They are compiled once and are case-insensitive.
_CONTRACT_SIGNALS = re.compile(
    r"\b(json|yaml|schema|must (?:be|include|contain|return|output)|exactly|"
    r"format|table|csv|only (?:output|return)|final line|bullet(?:ed)? list)\b",
    re.IGNORECASE,
)
_NUMBERED_REQ = re.compile(r"(?m)^\s*(?:\d+[.)]|-\s|\*\s)")
_PLANNING_SIGNALS = re.compile(
    r"\b(plan|step by step|step-by-step|decompose|break (?:this |it )?down|"
    r"design|architect|strategy|first .*then|multi-step)\b",
    re.IGNORECASE,
)
_AMBIGUITY_SIGNALS = re.compile(
    r"\b(maybe|somehow|not sure|unclear|figure out|something like|"
    r"or something|whatever works|etc\.?)\b",
    re.IGNORECASE,
)


@dataclass
class RouterPolicy:
    """Deterministic thresholds. Kept small and inspectable; loaded from
    :class:`GatewayConfig` at serve time so an operator can see/override them."""

    context_token_threshold: int = 4000
    # How many numbered/deterministic requirements before CHECK is considered.
    check_requirement_threshold: int = 3
    # Below this many input tokens with no other signal, always PASS_THROUGH.
    trivial_token_ceiling: int = 200
    # Bounded intervention budget reported with any non-passthrough decision.
    max_extra_latency_ms: int = 2500
    max_extra_tokens: int = 1200
    max_attempts: int = 2


@dataclass
class RouterDecision:
    """An auditable decision. ``features`` is the exact evidence it used."""

    decision: str
    reasons: list[str] = field(default_factory=list)
    confidence: float = 0.0
    intervention_budget: dict = field(default_factory=dict)
    features: dict = field(default_factory=dict)
    shadow: bool = True  # observe mode: recorded, never acted on

    def to_dict(self) -> dict:
        return asdict(self)


def extract_features(req: NormalizedRequest) -> dict:
    """Deterministically extract the signals the router reasons over."""
    text = req.all_text()
    input_tokens = req.input_tokens_est()
    contract_hits = len(_CONTRACT_SIGNALS.findall(text))
    numbered = len(_NUMBERED_REQ.findall(text))
    planning_hits = len(_PLANNING_SIGNALS.findall(text))
    ambiguity_hits = len(_AMBIGUITY_SIGNALS.findall(text))
    return {
        "input_tokens_est": input_tokens,
        "input_tokens_measured": False,
        "message_count": req.message_count(),
        "has_tools": req.has_tools(),
        "tool_count": len(req.tools),
        "has_images": req.has_images(),
        "stream": req.stream,
        "contract_signal_hits": contract_hits,
        "numbered_requirements": numbered,
        "planning_signal_hits": planning_hits,
        "ambiguity_signal_hits": ambiguity_hits,
    }


class CortexRouter:
    """Deterministic decision maker. ``decide`` is a pure function of the
    request and policy — no clock, no randomness, no network."""

    def __init__(self, policy: RouterPolicy | None = None):
        self.policy = policy or RouterPolicy()

    def decide(self, req: NormalizedRequest, *, shadow: bool = True) -> RouterDecision:
        p = self.policy
        f = extract_features(req)
        reasons: list[str] = []

        wants_context = f["input_tokens_est"] >= p.context_token_threshold
        deterministic_reqs = max(f["contract_signal_hits"], f["numbered_requirements"])
        wants_check = deterministic_reqs >= p.check_requirement_threshold
        wants_think = f["planning_signal_hits"] >= 1 and f["message_count"] <= 4

        # Trivial-and-clear requests always pass through. This is the
        # abstention-first default and it fires first.
        if (
            f["input_tokens_est"] <= p.trivial_token_ceiling
            and not wants_check
            and not wants_think
            and not wants_context
        ):
            reasons.append(
                f"input estimate {f['input_tokens_est']} tokens is below trivial "
                f"ceiling {p.trivial_token_ceiling} and no intervention signal fired"
            )
            return self._mk("PASS_THROUGH", reasons, 0.9, f, shadow, budget=False)

        if wants_context:
            reasons.append(
                f"input estimate {f['input_tokens_est']} tokens >= context "
                f"threshold {p.context_token_threshold}"
            )
        if wants_check:
            reasons.append(
                f"{deterministic_reqs} deterministic output requirement(s) detected "
                f"(>= threshold {p.check_requirement_threshold})"
            )
        if wants_think:
            reasons.append(
                f"{f['planning_signal_hits']} planning signal(s) on a short "
                f"conversation ({f['message_count']} message(s))"
            )
        if f["ambiguity_signal_hits"]:
            reasons.append(
                f"{f['ambiguity_signal_hits']} ambiguity signal(s) present"
            )

        decision = self._combine(wants_think, wants_context, wants_check)
        if decision == "PASS_THROUGH":
            reasons.append("no intervention signal cleared its threshold")
            return self._mk("PASS_THROUGH", reasons, 0.75, f, shadow, budget=False)

        # Confidence is a bounded, explainable heuristic: more independent
        # signals firing -> higher confidence, capped.
        n_signals = sum([wants_think, wants_context, wants_check])
        confidence = min(0.6 + 0.12 * n_signals, 0.95)
        return self._mk(decision, reasons, confidence, f, shadow, budget=True)

    def _combine(self, think: bool, context: bool, check: bool) -> str:
        if think and context and check:
            return "FULL_CORTEX"
        if context and check:
            return "CONTEXT_AND_CHECK"
        if think and context:
            return "THINK_AND_CONTEXT"
        if think:
            return "THINK"
        if context:
            return "CONTEXT"
        if check:
            return "CHECK"
        return "PASS_THROUGH"

    def _mk(
        self,
        decision: str,
        reasons: list[str],
        confidence: float,
        features: dict,
        shadow: bool,
        *,
        budget: bool,
    ) -> RouterDecision:
        p = self.policy
        ib: dict = {}
        if budget:
            ib = {
                "max_extra_latency_ms": p.max_extra_latency_ms,
                "max_extra_tokens": p.max_extra_tokens,
                "max_attempts": p.max_attempts,
            }
        return RouterDecision(
            decision=decision,
            reasons=reasons,
            confidence=round(confidence, 2),
            intervention_budget=ib,
            features=features,
            shadow=shadow,
        )
