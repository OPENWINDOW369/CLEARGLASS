"""Policy Decision Point client. Wraps OPA/Cedar in production; local stub here."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PolicyDecision:
    allow: bool
    reason: str
    decision_id: str


_CLEARANCE = {"UNCL": 0, "CONF": 1, "SECRET": 2, "TS": 3}


def policy_check(*, actor_id: str, action: str, actor: dict, resource: dict, context: dict | None = None) -> PolicyDecision:
    context = context or {}
    actor_rank = _CLEARANCE.get(actor.get("clearance", "UNCL"), 0)
    res_rank = _CLEARANCE.get(resource.get("classification", "UNCL"), 0)
    if actor_rank < res_rank:
        return PolicyDecision(False, "insufficient clearance", f"pdp-{actor_id}-{action}")

    actor_scope = set(actor.get("coalition_scope", []))
    res_scope = set(resource.get("coalition_scope", []))
    if res_scope and not (actor_scope & res_scope):
        return PolicyDecision(False, "coalition boundary violation", f"pdp-{actor_id}-{action}")

    if action == "action.execute":
        if not context.get("human_approval_token"):
            return PolicyDecision(False, "missing human approval token", f"pdp-{actor_id}-{action}")
        if context.get("confidence", 0.0) < 0.8:
            return PolicyDecision(False, "confidence below threshold", f"pdp-{actor_id}-{action}")

    return PolicyDecision(True, "ok", f"pdp-{actor_id}-{action}")
