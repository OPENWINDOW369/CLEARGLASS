// Thin event-bus shim. Swap for a Kafka/Redpanda producer in production.
export async function publish(topic, message) {
  // eslint-disable-next-line no-console
  console.log(`[bus] ${topic}`, JSON.stringify(message));
}
