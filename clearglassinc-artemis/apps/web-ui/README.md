# web-ui (stub)

Next.js + TypeScript operator UI. Planned modules:

- `GraphView` — entity network, filtered by `policy_binding_id`.
- `CaseWorkbench` — case timeline + evidence.
- `CopilotPanel` — AIP chat + tool cards.
- `ApprovalQueue` — operational approval gates (approve/reject action packages).
- `RevenueOpsDashboard` — Stripe + Gumroad + affiliate KPIs.

Scaffold with `npx create-next-app@latest .` then wire to `api-node` at `/v1/*`.
