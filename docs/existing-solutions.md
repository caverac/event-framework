# Existing Solutions

Several existing solutions provide event-driven architectures and frameworks. Below are some notable ones:

- [Lagom](https://www.lagomframework.com/) / [Akka Typed](https://akka.io/) (JVM): Event-sourced entities with persistent state, projections, message routing; strong on process & streams.

- [Eventuate](https://eventuate.io/) / [EventStoreDB](https://www.eventstore.com/) patterns: Opinionated event stores plus libraries for aggregates and sagas.

- [NServiceBus](https://particular.net/nservicebus) / [MassTransit](https://masstransit-project.com/) (.NET): Message routing, sagas, retries, idempotency; event-driven services with DDD flavors.

- [Temporal](https://temporal.io/) / [Cadence](https://github.com/uber/cadence) (polyglot): Durable workflows (saga-like) with strong process guarantees; you’d still layer aggregates on top.

- [Kafka Streams](https://kafka.apache.org/documentation/streams) / [ksqlDB](https://ksqldb.io/): Stream processing & projections via topics; you supply the aggregate logic.

In Python specifically, you’ll find smaller libs/patterns rather than one "Axon-scale" stack:

- [eventsourcing (python-eventsourcing)](https://github.com/johnbywater/eventsourcing): event-sourced aggregates, repositories, snapshots.

- [Faust](https://github.com/robinhood/faust) (stream processing): handler-centric Kafka apps (more data-flow than DDD, but pairs well).

- [Nameko](https://github.com/nameko/nameko) / [Dramatiq](https://dramatiq.io/) / [Celery](https://docs.celeryproject.org/): message-driven tasks; you’d layer DDD patterns atop.
