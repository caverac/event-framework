# Existing Solutions

Several existing solutions provide event-driven architectures and frameworks. Below are some notable ones:

- Axon Framework (Java/Kotlin): Aggregates, Commands, Events, Sagas, Event Store, Projections; pluggable buses. Very close if you rename your pieces to DDD terms.

- Lagom / Akka Typed (JVM): Event-sourced entities with persistent state, projections, message routing; strong on process & streams.

- Eventuate / EventStoreDB patterns: Opinionated event stores plus libraries for aggregates and sagas.

- NServiceBus / MassTransit (.NET): Message routing, sagas, retries, idempotency; event-driven services with DDD flavors.

- Temporal / Cadence (polyglot): Durable workflows (saga-like) with strong process guarantees; you’d still layer aggregates on top.

- Kafka Streams / ksqlDB: Stream processing & projections via topics; you supply the aggregate logic.

In Python specifically, you’ll find smaller libs/patterns rather than one “Axon-scale” stack:

- eventsourcing (library): event-sourced aggregates, repositories, snapshots.

- faust (stream processing): handler-centric Kafka apps (more data-flow than DDD, but pairs well).

- nameko / dramatiq / celery: message-driven tasks; you’d layer DDD patterns atop.