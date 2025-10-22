# Building the framework (Part II)

In the previous section we discussed with detail the notions of Actual Occasion and Prehension, we also built core abstractions to represnet them in code. To wire them up we created two simple disposable functions : `install(...)` and `run(...)` to help us bind prehensions to their subjects and run a simple breadth-first processing loop respectively.

Now we can discuss the last piece of the puzzle: the Nexus, which will help us organize multiple occasions and route data between them.

## Nexus
A nexus is a togetherness--a pattern or grouping--of actual occasions that are related by how they prehend one another. It is not a new fundamental unit (that's the actual occasion); it's the organized many formed by their relations. 

### Key traits

- **Many-made-one (pattern)**: A nexus is a set of occasions bound by relevant prehensions—"this lot hangs together."
- **Relational coherence**: The unity comes from recurrent relational patterns (who feels whom, how strongly, in what way).
- **Not fundamental**: The actual occasion is the basic unit; a nexus is composed of occasions.
- **Degrees & kinds**: There can be loose nexūs (fleeting clusters) or stable, rule-governed ones. A society is a special nexus with a persistent "social order" (a characteristic pattern that endures across many occasions).
- **Regioned/located**: A nexus can be described over a region (spatiotemporal, conceptual, organizational) where its pattern holds.
- **Open-ended**: Membership can change as new occasions arise and old ones perish; the pattern can strengthen, weaken, bifurcate, or dissolve.

### Examples

- **A conversation circle**:
The quick back-and-forth utterances are individual occasions. The nexus is the conversational group with its cues, shared topic, and rhythms that bind these moments into a recognizable whole.

- **A morning commute traffic cluster**:
Each driver's micro-decisions (occasions) relate through braking, merging, pacing. The nexus is the congestion pattern—its formation, wave propagation, and dissipation over a stretch of road.

- **A classroom session**:
Moments of attention, questions, and explanations are occasions; the nexus is the class as it unfolds—a coordinated pattern with a shared aim and recognizable order (syllabus, norms).

### Examples to software 

These are analogies. In software we talk about events (records/messages) and state updates; an "actual occasion" maps best to a *bounded act of processing* that consumes prior facts and yields a new concrete result.

- **A bounded context reacting to a stream**:
Each handler invocation (occasion) prehends domain facts; the nexus is the context's working pattern—its consistent language, invariants, and subscriptions that make those invocations cohere.

- **A distributed trace of one request**:
Every span in services A→B→C is an occasion. The full trace—causal links, timings, retries—is a nexus (a structured region of related processing).

- **An ECS service during a batch run**:
Each task execution is an occasion; the fleet pattern (autoscaling behavior, shared configuration, coordinated checkpoints) is the nexus that gives those tasks a recognizable, persistent order.

- **An event-sourced read model**:
Each projection step (occasion) takes up a fact; the read model as a whole, with its stable schema and consistent replay rules, is a nexus—a society of processing acts that yields a durable pattern.

## Let's finish the code

### Defining the Nexus abstraction
A nexus is our abstraction to organize and orchestrate multiple occasions. It will help us route data between occasions based on their prehensions. It should then provide an API to:

- Register occasions

- Route data between occasions based on their prehensions

- Emit resulting data from occasions to the outside world

Here is a possible implementation:

```python
class Nexus:
    def __init__(self, name: str):
        self.name = name
        self._occasions: dict[str, ActualOccasion] = {}
        self._middlewares: list[Callable[[Datum], Datum]] = []

    def add(self, *occasions: ActualOccasion) -> "Nexus":
        for occ in occasions:
            self._occasions[occ.name] = occ
        return self

    def bind(self, *prehensions: Prehension) -> "Nexus":
        for ph in prehensions:
            ph.subject.on(ph.selector, ph.form)
        return self

    def use(self, middleware: Callable[[Datum], Datum]) -> "Nexus":
        self._middlewares.append(middleware)
        return self

    def _apply_middlewares(self, d: Datum) -> Datum:
        for mw in self._middlewares:
            d = mw(d)
        return d

    def emit(self, *data: Datum) -> list[Datum]:
        queue: list[Datum] = [self._apply_middlewares(d) for d in data]
        seen: list[Datum] = []

        while queue:
            current = queue.pop(0)
            seen.append(current)

            # Let every occasion prehend this datum
            for occ in self._occasions.values():
                derived = list(occ.handle(current))

                # Thread causation/correlation ids
                derived = [
                    Datum(
                        name=d.name,
                        payload=d.payload,
                        correlation_id=current.correlation_id or current.id,
                        causation_id=current.id,
                        id=d.id,
                    )
                    for d in derived
                ]

                queue.extend(self._apply_middlewares(d) for d in derived)

        return seen

    def snapshot(self) -> dict[str, dict[str, Any]]:
        return {name: occ.state for name, occ in self._occasions.items()}

```

### Back to our payment processing example
To build the nexus we just need

```python
nexus = (
    Nexus("Commerce")
    .add(payments, decision, audit)
    .bind(
        Prehension(payments, by_name("OrderPlaced"), consider_payment),
        Prehension(decision, by_name("PaymentAuthorized"), record_outcome),
        Prehension(decision, by_name("PaymentDeclined"), record_outcome),
        Prehension(audit, lambda _d: True, audit_everything),
    )
)
```

Intuitively speaking, we have created a nexus called "Commerce", a room where messages come in and get routed. We add the participants (`payments`, `decision`, `audit`) to the room, each can react to certain messages.
We then bind the rules for who reacts to what, those are what the prehensions define. *when this kind of mssage arrives, let this particular actor feel it in this way*, e.g., when an order is placed, the payments actor evaluates (approve/decline) the payment.

> "Set up a `Commerce` room with three actors.If an order is placed, Payments evaluates it.
If an order is placed, Payments evaluates it.
If a payment is authorized or declined, OrderDecision records the result.
And no matter what happens, Audit logs it all."

Let's create a little middleware to ensure correlation ids are threaded through:

```python
def thread_correlation(datum: Datum) -> Datum:
    return Datum(
        name=datum.name,
        payload=datum.payload,
        correlation_id=datum.correlation_id or datum.id,
        causation_id=datum.causation_id,
        id=datum.id,
    )
nexus.use(thread_correlation)
```

And that's it! We can now run the nexus by emitting an initial datum:

```python
closure = nexus.emit(
    Datum("OrderPlaced", {"order_id": "A-100", "total": 420.0}, id="d1"),
    Datum("OrderPlaced", {"order_id": "B-200", "total": 640.0}, id="d2"),
)
```

We can use the little utility method `snapshot()` to see the final state of each occasion in the nexus:

```python
for name, st in nexus.snapshot().items():
    print(name, "=>", st)
```

This will print

```shell
Payments => {'limit': 500.0, 'decisions': {'A-100': {'amount': 420.0, 'approved': True}, 'B-200': {'amount': 640.0, 'approved': False}}}
OrderDecision => {'orders': {'A-100': {'status': 'ACCEPTED'}, 'B-200': {'status': 'REJECTED'}}}
Audit => {'events': [('OrderPlaced', {'order_id': 'A-100', 'total': 420.0}), ('OrderPlaced', {'order_id': 'B-200', 'total': 640.0}), ('PaymentAuthorized', {'order_id': 'A-100', 'amount': 420.0}), ('PaymentDeclined', {'order_id': 'B-200', 'amount': 640.0})]}
```

Note, for example, how the Payments occasion recorded both decisions (approved and declined) based on the initial orders placed. The OrderDecision occasion then recorded the final status of each order, and the Audit occasion logged all events that transpired in the nexus.

### Final thoughts
- We got rid of the disposable `install(...)` and `run(...)` functions by encapsulating their logic within the Nexus abstraction.
- The Nexus now serves as the orchestrator of occasions, managing their registration, prehension bindings, and data routing.
- This design allows us to easily extend the system by adding more occasions and prehensions without changing the core processing loop.
- The middleware mechanism provides a flexible way to manipulate data as it flows through the nexus, enabling cross-cutting concerns like logging, tracing, or validation.
- The API is fluent and expressive, making it easy to understand the structure and behavior of the nexus at a glance.