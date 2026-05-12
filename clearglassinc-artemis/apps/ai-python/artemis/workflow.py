"""Case workflow state machine (Temporal-style, in-memory reference impl)."""
from __future__ import annotations

from enum import Enum


class State(str, Enum):
    INGESTED = "INGESTED"
    TRIAGED = "TRIAGED"
    ENRICHED = "ENRICHED"
    CORRELATED = "CORRELATED"
    RECOMMENDED = "RECOMMENDED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"
    ROLLED_BACK = "ROLLED_BACK"


TRANSITIONS: dict[State, list[State]] = {
    State.INGESTED: [State.TRIAGED],
    State.TRIAGED: [State.ENRICHED, State.CLOSED],
    State.ENRICHED: [State.CORRELATED],
    State.CORRELATED: [State.RECOMMENDED],
    State.RECOMMENDED: [State.AWAITING_APPROVAL],
    State.AWAITING_APPROVAL: [State.EXECUTED, State.REJECTED],
    State.EXECUTED: [State.CLOSED, State.ROLLED_BACK],
    State.REJECTED: [State.CLOSED],
}


class IllegalTransition(RuntimeError):
    pass


def transition(current: State, target: State) -> State:
    if target not in TRANSITIONS.get(current, []):
        raise IllegalTransition(f"{current} -> {target} is not allowed")
    return target
