"""Multi-agent orchestration: triage -> enrich -> correlate -> recommend -> compliance gate.

No agent self-authorizes execution. The orchestrator always returns a pending
human-approval task for operationally significant actions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from artemis.policy import policy_check
from artemis import tools


@dataclass
class AgentContext:
    actor_id: str
    coalition_scope: list[str]
    clearance: str
    case_id: str | None = None
    mfa_enabled: bool = True


@dataclass
class Recommendation:
    summary: str
    confidence: float
    actions: list[dict[str, Any]] = field(default_factory=list)


def _actor_dict(ctx: AgentContext) -> dict[str, Any]:
    return {
        "clearance": ctx.clearance,
        "coalition_scope": ctx.coalition_scope,
        "mfa_enabled": ctx.mfa_enabled,
        "role": "analyst",
    }


def triage_and_recommend(event: dict[str, Any], ctx: AgentContext) -> dict[str, Any]:
    classification = event.get("classification", "UNCL")
    coalition_scope = event.get("coalition_scope", [])

    # 1. Read policy gate before any enrichment read.
    read_decision = policy_check(
        actor_id=ctx.actor_id,
        action="ontology.read",
        actor=_actor_dict(ctx),
        resource={"classification": classification, "coalition_scope": coalition_scope},
    )
    if not read_decision.allow:
        return {"status": "denied", "reason": read_decision.reason}

    # 2. Enrichment + correlation (stubbed tools).
    entities = tools.foundry_query({"event_id": event.get("id"), "scope": ctx.coalition_scope})
    links = tools.gotham_entity_lookup({"entities": entities["entities"], "max_hops": 2})

    # 3. Recommendation draft.
    rec = Recommendation(
        summary=f"Potential coordinated activity around {event.get('id')}",
        confidence=0.84,
        actions=[{"type": "OPEN_CASE", "payload": {"priority": "high"}}],
    )

    # 4. Compliance gate for the action — note: no execution here.
    exec_decision = policy_check(
        actor_id=ctx.actor_id,
        action="case.open",
        actor=_actor_dict(ctx),
        resource={"classification": classification, "coalition_scope": coalition_scope},
    )
    if not exec_decision.allow:
        return {"status": "denied", "reason": exec_decision.reason, "recommendation": rec.__dict__}

    return {
        "status": "awaiting_human_approval",
        "recommendation": rec.__dict__,
        "policy_decision_id": exec_decision.decision_id,
        "links": links,
    }
