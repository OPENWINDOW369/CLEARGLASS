import express from "express";
import crypto from "node:crypto";
import { redis } from "./redis.js";
import { publish } from "./bus.js";

const app = express();

// --- Webhook ingress with idempotency -------------------------------------
async function handleWebhook(provider, req, res) {
  const sig = req.headers[`${provider}-signature`];
  if (!sig) return res.status(400).send("missing signature");
  // NOTE: real signature verification (Stripe/Gumroad SDK) goes here.
  let event;
  try {
    event = JSON.parse(req.body.toString());
  } catch {
    return res.status(400).send("bad payload");
  }
  const idemKey = `idem:${provider}:${event.id}`;
  if (await redis.get(idemKey)) return res.status(200).send("duplicate");
  await redis.set(idemKey, "1", "EX", 86400);
  await publish("billing.subscription.events", { provider, event });
  return res.status(202).send("accepted");
}

app.post("/v1/webhooks/stripe", express.raw({ type: "application/json" }), (req, res) =>
  handleWebhook("stripe", req, res)
);
app.post("/v1/webhooks/gumroad", express.raw({ type: "application/json" }), (req, res) =>
  handleWebhook("gumroad", req, res)
);

// --- Event ingest ----------------------------------------------------------
app.post("/v1/events/ingest", express.json(), async (req, res) => {
  const id = req.body.id ?? crypto.randomUUID();
  await publish("intel.raw.events", { ...req.body, id });
  res.status(202).json({ accepted: true, id });
});

// --- Approval gates (stubs) ------------------------------------------------
app.post("/v1/actions/:id/approve", express.json(), async (req, res) => {
  await publish("intel.case.actions", { action_id: req.params.id, decision: "approved", actor: req.body.actor });
  res.json({ ok: true });
});
app.post("/v1/actions/:id/reject", express.json(), async (req, res) => {
  await publish("intel.case.actions", { action_id: req.params.id, decision: "rejected", actor: req.body.actor });
  res.json({ ok: true });
});

app.get("/healthz", (_req, res) => res.json({ ok: true }));

const port = process.env.PORT ?? 8080;
app.listen(port, () => console.log(`api-node listening on :${port}`));

export { app };
