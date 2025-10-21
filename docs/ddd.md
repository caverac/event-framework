# Domain Driven Design

Now that we completed the foundational aspects of the event-framework, it's essential to understand how Domain Driven Design (DDD) principles are integrated into its architecture. DDD focuses on modeling software based on the complex needs of the business domain, ensuring that the code reflects real-world processes and rules.

## Big differences (and overlaps)

**DDD**: centers on ubiquitous language, bounded contexts, aggregates/invariants, and strategic design (context maps). Events are important, but they’re in service of the model.

**Our framework**: centers on process/becoming: Occasions (subjects that react), Prehensions (rules for how/when they react), Nexus (the room/router), Datum (facts). It’s event-oriented by construction and very composable.

### Mapping of core pieces

| Our framework | DDD-ish analogue | Notes |
| ------------- | ---------------- | ----- |
| **Datum** | Domain Event (fact) | We intentionally kept "Datum" neutral; can be persisted/transported like events. |
| **Occasion** | Aggregate / Policy / Projection | Pick per role: invariants → Aggregate; emits follow-ups → Policy; builds read models → Projection. |
| **Prehension (selector + form)** | Subscription / Handler / Policy | Separates *relevance* (selector) from *reaction* (form). Very testable. |
| **Nexus** | In-process Event Bus (per bounded context) | Routes facts to subjects; where middlewares live. |

### What our framework does well
- **Edge-first behavior**. Encodes when and how reactions happen as first-class objects (prehensions).
- **Composability**. Add/remove behavior without modifying core classes.
- **Replay & determinism friendly**. Facts-in → reactions → new facts out.
- **Pedagogical clarity**. “Who reacts, to what, and how” reads almost like prose.

### What classic DDD brings that we haven't formalized

- Aggregates with explicit invariants & transactional boundaries.
- Commands vs. Events separation (intent vs. fact) and a command handler layer.
- Repositories and persistence patterns (Event Store + snapshots, or CRUD).
- Sagas/Process Managers for long-running, cross-aggregate workflows.
- Strategic design: bounded contexts, context maps, anti-corruption layers.
- Schema/versioning, idempotency, error handling, retries, exactly/at-least-once semantics.
- Observability baked in (tracing/metrics/logging contracts).

## What to add to make it a complete DDD framework

This may represent future work, but here are some ideas:

### Tactical building blocks

- Command type (separate from Datum/Event) + Command Handlers: Distinguish intent (AuthorizePayment) from fact (PaymentAuthorized).

- Aggregate base with invariant checks and a decision method
e.g., apply(command) -> [events], evolve(state, event) -> state. Prevent illegal transitions.

- Repository interfaces: load(aggregate_id) -> state, commit(events, expected_version). Add optimistic concurrency & versioning.

- Event Store + snapshots: Pluggable backends (in-memory, Postgres, Dynamo, S3+Parquet).

- Projection & Read Model support: Rebuildable, idempotent; fan-out from your Nexus.

### Process orchestration

- Saga / Process Manager abstraction: Correlate by correlation_id, manage timeouts, compensations, retries.

- Boundary adapters (ACL):
Anti-corruption layers between bounded contexts (translation prehensions).

### Runtime and non-functionals

- Middlewares (already started) for dedupe, authZ, tracing, schema upgrades.

- Error policy: retry, backoff, DLQ; idempotency keys.

- Schema/contract versioning: Event/Datum version field + upcasters/downcasters.

- Testing scaffolding: Given–When–Then harness: (given events) + (when command) => (expect events/state). Given–When–Then harness: `(given events) + (when command) => (expect events/state)`.

### API ergonomics

- Context Bus interface that can be backed by real infra
(in-proc Nexus today; SQS/SNS/Kafka/Kinesis tomorrow) with the same programming model.

- Developer DX
generators for aggregates/projections/sagas; a tiny CLI to replay, inspect streams, and scaffold contexts.