# admin-rails (stub)

Rails admin/ops back office: subscriptions, refunds, affiliate payouts, compliance.
Only the policy-aware controller + model skeletons are included here. Run `rails new`
into this directory (or copy these files into an existing app) to bootstrap.

Key invariants:
- Every operationally significant admin action writes an `AuditLog` row in the same transaction.
- Billing actions require MFA + `admin` role + a policy pass (`authorize_action!`).
