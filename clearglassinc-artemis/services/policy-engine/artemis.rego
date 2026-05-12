package artemis.authz

# Default deny. Every read, tool call, and action execution must be explicitly allowed.
default allow = false

# Coalition overlap helper.
coalition_overlap {
  some i, j
  input.actor.coalition_scope[i] == input.resource.coalition_scope[j]
}

# Clearance lattice.
clearance_rank := {"UNCL": 0, "CONF": 1, "SECRET": 2, "TS": 3}
actor_clears {
  clearance_rank[input.actor.clearance] >= clearance_rank[input.resource.classification]
}

# Open a case.
allow {
  input.action == "case.open"
  actor_clears
  coalition_overlap
}

# Read an ontology object.
allow {
  input.action == "ontology.read"
  actor_clears
  coalition_overlap
}

# Execute an approved action package — requires a human approval token.
allow {
  input.action == "action.execute"
  actor_clears
  coalition_overlap
  input.context.human_approval_token != ""
  input.context.confidence >= 0.8
}

# Admin billing actions require MFA.
allow {
  startswith(input.action, "billing.")
  input.actor.mfa_enabled == true
  input.actor.role == "admin"
}
