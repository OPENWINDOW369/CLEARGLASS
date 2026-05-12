# Runbook: AI artifact rollback

Triggered automatically by drift monitor or manually by the on-call operator.

## Auto-rollback conditions
- precision < 0.82
- latency p95 > 1800 ms
- operator trust score < 4.0
- false positive rate > 0.18

## Steps
1. Apollo halts the in-progress rollout.
2. Traffic pinned to last stable `prompt_bundle` / `routing_policy` / `agent_workflow_graph`.
3. Incident ticket auto-created with the offending candidate version IDs.
4. Candidate quarantined; cannot be re-promoted without Human Review Board sign-off.
5. Post-incident: attach decision traces + eval deltas to the audit record.
