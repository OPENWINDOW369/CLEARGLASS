from artemis.agents.orchestrator import AgentContext, triage_and_recommend
from artemis.evals.pipeline import EvalReport, propose_upgrade, should_rollback
from artemis.workflow import State, transition, IllegalTransition

import pytest


def test_orchestrator_returns_pending_approval():
    ctx = AgentContext(actor_id="u1", coalition_scope=["US"], clearance="TS")
    out = triage_and_recommend({"id": "evt-1", "classification": "SECRET", "coalition_scope": ["US"]}, ctx)
    assert out["status"] == "awaiting_human_approval"


def test_orchestrator_denies_on_coalition_mismatch():
    ctx = AgentContext(actor_id="u2", coalition_scope=["ALLY_X"], clearance="TS")
    out = triage_and_recommend({"id": "evt-2", "classification": "SECRET", "coalition_scope": ["US"]}, ctx)
    assert out["status"] == "denied"


def test_workflow_transitions():
    assert transition(State.INGESTED, State.TRIAGED) == State.TRIAGED
    with pytest.raises(IllegalTransition):
        transition(State.INGESTED, State.EXECUTED)


def test_rollback_and_proposal():
    assert should_rollback({"precision": 0.5})
    assert not should_rollback({"precision": 0.95, "latency_p95_ms": 900, "false_positive_rate": 0.05})
    assert propose_upgrade(EvalReport("prompt_bundle:v58", 0.9, 0.9, 900, 0.05, precision_delta=0.04, latency_delta=0.01))
    assert propose_upgrade(EvalReport("prompt_bundle:v59", 0.9, 0.9, 900, 0.05, precision_delta=0.0)) is None
