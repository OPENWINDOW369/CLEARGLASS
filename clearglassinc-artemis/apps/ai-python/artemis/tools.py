"""Approved tool contracts. Agents may only act through these."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ToolName = Literal[
    "foundry_query",
    "gotham_entity_lookup",
    "open_case",
    "draft_action_package",
    "notify_commander",
    "stripe_create_checkout",
    "gumroad_fulfill_asset",
]


class ToolRequest(BaseModel):
    tool_name: ToolName
    arguments: dict[str, Any]
    reason: str = Field(min_length=10)
    actor_id: str
    case_id: str | None = None
    requires_approval: bool = True


class ToolResponse(BaseModel):
    status: Literal["ok", "denied", "error"]
    data: dict[str, Any] = {}
    policy_decision_id: str | None = None
    error: str | None = None


# --- Stub implementations -------------------------------------------------
def foundry_query(args: dict[str, Any]) -> dict[str, Any]:
    return {"entities": [], "query": args}


def gotham_entity_lookup(args: dict[str, Any]) -> dict[str, Any]:
    return {"links": [], "query": args}


def open_case(args: dict[str, Any]) -> dict[str, Any]:
    return {"case_id": "stub-case", "args": args}
