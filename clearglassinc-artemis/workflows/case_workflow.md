# Case workflow (Temporal-style)

States: `INGESTED, TRIAGED, ENRICHED, CORRELATED, RECOMMENDED, AWAITING_APPROVAL, EXECUTED, REJECTED, CLOSED, ROLLED_BACK`

Transitions:

| From | To |
|---|---|
| INGESTED | TRIAGED |
| TRIAGED | ENRICHED, CLOSED |
| ENRICHED | CORRELATED |
| CORRELATED | RECOMMENDED |
| RECOMMENDED | AWAITING_APPROVAL |
| AWAITING_APPROVAL | EXECUTED, REJECTED |
| EXECUTED | CLOSED, ROLLED_BACK |
| REJECTED | CLOSED |

Reference implementation: `apps/ai-python/artemis/workflow.py`.
Topics consumed/produced: `intel.raw.events`, `intel.alerts`, `intel.case.actions`, `ai.eval.inputs`.
