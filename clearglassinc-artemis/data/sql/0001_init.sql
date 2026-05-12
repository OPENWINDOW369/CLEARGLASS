-- ClearGlassInc Artemis — initial schema
-- Postgres 15+

create extension if not exists "uuid-ossp";

-- Identity & access
create table iam_principals (
  principal_id uuid primary key default uuid_generate_v4(),
  principal_type text not null check (principal_type in ('user','service')),
  email text unique,
  role text not null,
  coalition_scope text[] not null default '{}',
  clearance_level text not null,
  mfa_enabled boolean not null default true,
  created_at timestamptz not null default now()
);

create table api_tokens (
  id uuid primary key default uuid_generate_v4(),
  principal_id uuid not null references iam_principals(principal_id),
  token_hash text not null,
  scope text[] not null,
  expires_at timestamptz not null,
  revoked_at timestamptz
);

-- Policy bindings
create table policy_bindings (
  policy_binding_id uuid primary key default uuid_generate_v4(),
  resource_type text not null,
  row_acl jsonb not null default '{}',
  column_acl jsonb not null default '{}',
  action_acl jsonb not null default '{}',
  created_at timestamptz not null default now()
);

-- Billing / monetization
create table subscriptions (
  id uuid primary key default uuid_generate_v4(),
  principal_id uuid not null references iam_principals(principal_id),
  provider text not null check (provider in ('stripe','gumroad')),
  provider_customer_id text not null,
  plan_code text not null,
  status text not null check (status in ('trialing','active','past_due','canceled')),
  renews_at timestamptz,
  policy_binding_id uuid references policy_bindings(policy_binding_id),
  created_at timestamptz not null default now()
);

-- Ontology
create table ontology_objects (
  object_id uuid primary key default uuid_generate_v4(),
  object_type text not null,
  payload jsonb not null,
  confidence numeric(5,4) not null check (confidence >= 0 and confidence <= 1),
  lineage jsonb not null,
  valid_from timestamptz,
  valid_to timestamptz,
  classification text not null check (classification in ('UNCL','CONF','SECRET','TS')),
  coalition_scope text[] not null default '{}',
  policy_binding_id uuid references policy_bindings(policy_binding_id),
  provenance_hash text,
  created_at timestamptz not null default now()
);

create table ontology_relationships (
  rel_id uuid primary key default uuid_generate_v4(),
  from_object_id uuid not null references ontology_objects(object_id),
  to_object_id uuid not null references ontology_objects(object_id),
  rel_type text not null,
  confidence numeric(5,4) not null check (confidence >= 0 and confidence <= 1),
  evidence jsonb not null,
  observed_at timestamptz,
  policy_binding_id uuid references policy_bindings(policy_binding_id),
  created_at timestamptz not null default now()
);
create index on ontology_relationships (from_object_id);
create index on ontology_relationships (to_object_id);

-- Workflow / cases
create table case_workflows (
  case_id uuid primary key default uuid_generate_v4(),
  state text not null default 'INGESTED',
  event_payload jsonb not null,
  classification text not null,
  coalition_scope text[] not null default '{}',
  prompt_bundle_version text,
  routing_policy_version text,
  workflow_graph_version text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Immutable-ish audit pointer (true WORM store lives in audit-ledger service)
create table audit_log (
  id bigserial primary key,
  actor_id uuid,
  action text not null,
  target_type text,
  target_id text,
  policy_decision_id text,
  metadata jsonb not null default '{}',
  prev_hash text,
  entry_hash text not null,
  created_at timestamptz not null default now()
);
