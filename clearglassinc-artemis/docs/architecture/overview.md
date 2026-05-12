# Architecture Overview

## Layers

1. **UI** — Analyst Workbench, Commander COP, Admin/Billing.
2. **API edge / zero-trust** — Cloudflare WAF/CDN, API gateway, CAPTCHA, rate limits.
3. **Identity & policy** — OIDC/SAML/MFA auth, OPA/Cedar PDP, immutable audit ledger.
4. **Core services** — Node API/BFF, Rails admin/ops, Python AI orchestrator.
5. **Event mesh** — Kafka/Redpanda + Redis Streams + Temporal workflows + DLQs.
6. **Data plane** — PostgreSQL (OLTP), Redis (cache/limits), lakehouse, OpenSearch/pgvector RAG.
7. **Palantir** — Gotham (case ops), Foundry (ontology/pipelines), AIP (copilots/agents/evals), Apollo (deploy/rollback).
8. **External** — Stripe, Gumroad, affiliate network, TikTok/Meta/GA4 pixels, email/CRM.

## Tech mapping

| Concern | Tech |
|---|---|
| Public API / BFF / webhooks | Node.js |
| Admin / subscriptions / refunds / compliance | Ruby on Rails |
| Agent runtime / evals / model router / self-improvement | Python |
| OLTP / billing / audit pointers | PostgreSQL |
| Rate limits / queues / sessions / idempotency | Redis |
| Containers | Docker (signed images, SBOM) |
| CI/CD | GitHub Actions + Apollo |
| Edge | Cloudflare (WAF/CDN/Zero Trust) |

## Workflow state machine

`INGESTED → TRIAGED → ENRICHED → CORRELATED → RECOMMENDED → AWAITING_APPROVAL → EXECUTED → CLOSED | ROLLED_BACK`
(`TRIAGED → CLOSED`, `AWAITING_APPROVAL → REJECTED` also valid.)

## Self-improvement loop

Capture → Evaluate (offline) → Propose (prompt/workflow/routing candidates) →
Sandbox A/B (shadow + canary) → Human Review Board → Promote via Apollo (staged) →
Drift monitor (auto-rollback). Versioned artifacts: `prompt_bundle:vNN`, `agent_workflow_graph:vNN`,
`routing_policy:vNN`, `eval_suite:vNN`, `policy_pack:vNN`.

## Security & governance

Zero-trust mTLS mesh, ontology ACL-tag-driven row/column/entity permissions, coalition
boundary enforcement via policy-as-code, WORM + hash-chained audit logs, token rotate/expire/revoke,
behavioral fraud scoring, PITR backups + DR drills, runtime kill switches / cost budgets / max exec time.
