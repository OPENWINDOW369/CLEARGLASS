import Redis from "ioredis";

// Single shared connection; falls back to localhost for dev.
export const redis = new Redis(process.env.REDIS_URL ?? "redis://localhost:6379");
