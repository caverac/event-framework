# Building the framework (part 1)

We will start by going through the steps to build the framework from scratch.
This will give you a good understanding of how the pieces fit together, from the core
abstractions of Whitehead's cosmology to the actual python code.

## Actual Occasion
An actual occasion—also called an *actual entity*—is, for Whitehead, the fundamental unit of reality: a tiny act of becoming in which the world is taken up, integrated, and completed into one new concrete fact (a "satisfaction"). Everything else (objects, enduring things, laws) is derivative of patterns of such occasions.

### Key traits

- **Unit of reality**: The "final real things" are actual occasions. Larger things are societies/patterns made of many occasions; abstract things are ways occasions can be organized or felt.

- **Process, not substance**: An occasion is not a little lump of stuff; it's a *happening* with a beginning (taking in data), a middle (integrating it), and an end (a completed fact).

- **Internally relational**: Each occasion feels relevant data from the past (prehensions, will come back to this later) while becoming—but the occasion itself is the unit; those feelings are its ingredients, not separate building blocks.

- **Once-and-done**: An occasion happens once and is then complete. Persistence (like a person, a rock, or a running system) is a pattern of many occasions, not one occasion persisting. This is a key shift from object-oriented thinking.

### Examples

- **A flash of recognition**: You see a friend across the street and, in an instant, the sight, memory, and mood fuse into one concrete moment—"Oh! It's Bob!" That one unit of experience is an actual occasion.

- **A micro-decision**: You reach for the hot pan, notice the heat, and in that moment decide to grab a mitt. That tiny, integrated "feel → assess → decide" is an occasion.

- **A pang of regret that passes**: A text reminds you of something you forgot. The feeling rises, integrates with your current aims ("I'll fix it now"), and settles. That bounded episode of becoming is an occasion.

In each case, the occasion is not the long story ("my whole day") and not the abstract category ("recognition"); it's the single, concrete, integrated moment. 

In all these examples, the actual occasion is a small, self-contained process of taking relevant inputs, integrating them, and producing a new, concrete outcome. The occasions' act of feeling relevant data from the past during its becoming is called a *prehension*, which we will cover next. In the examples above, the occasions prehend (feel) relevant inputs like sensory data, memories, and current context to form their integrated outcomes.

### Examples to software 

These are analogies. In software we talk about events (records/messages) and state updates; an "actual occasion" maps best to a *bounded act of processing* that consumes prior facts and yields a new concrete result.

- **Bank application** — posting a transfer:

    - Inputs: a validated FundsTransferInitiated fact, current ledger balances, risk flags.
    - Becoming: the system integrates those inputs under its rules (limits, idempotency).
    - Completion: a posted transfer (new ledger entries) and a durable FundsTransferred fact.
    - Occasion-like unit: that single, coherent posting step—one act that takes the past into account, applies rules, and finishes into a new fact.

- **User logging strategy** — writing an audit record:

    - Inputs: a LoginSucceeded fact, user metadata, policy ("mask PII").
    - Becoming: the logger integrates the fact with policy (redaction, correlation id).
    - Completion: an immutable audit entry written to storage.
    - Occasion-like unit: that one audit write: it doesn’t persist as "an ongoing thing"; it happens and is done.

- **Orbit integration** — processing a run request:

    - Inputs: OrbitIntegrationRequested (ICs, potential version, integrator config).
    - Becoming: the worker computes the trajectory under those parameters.
    - Completion: trajectory written (e.g., S3), OrbitIntegrated fact with metrics.
    - Occasion-like unit: the one run from request to completed output. (Finer-grained: a single integrator step can also serve as the occasion if you model at that resolution.)

## Prehension

A prehension is an act of feeling by which an actual occasion (the unit of becoming) takes account of some datum from its past and gives it a specific how of relevance (its "subjective form"). Prehensions are the ingredients of an occasion’s becoming—they are not independent things floating around; they only exist as phases within an occasion.

### Key traits
- **Relational, not substantial**: A prehension is a directed relation: this subject-occasion → that datum.
- **Three poles**:

    - Subject – the actual occasion doing the feeling.
    - Datum – what is felt (typically prior occasions; sometimes abstract possibilities).
    - Subjective form – how it is felt (intensity, valuation, mode—e.g., welcomed, ignored, constrained).

- **Constitutive but not fundamental**: Occasions are the fundamental units; prehensions constitute (make up) the occasion’s process of becoming ("concrescence"). No occasion → no prehensions. A rather imperfect analogy is that of a molecule (occasion) made of bonds (prehensions)—the bonds don’t exist independently; they are just parts/relations inside the molecule.

- **Positive vs. negative**: A prehension can include a datum (positive) or exclude it (negative)—exclusion still counts as a felt relation ("this does not matter for me now").

- **Many-to-one integration**: An occasion performs many prehensions and integrates their results into one completed fact ("satisfaction").


### Examples
- **Noticing a friend (positive prehension)**:
    - Subject = your current moment of experience
    - Datum = the prior fact of your friend’s presence
    - Subjective form = recognition-with-joy. You take up that datum and it shapes this moment.

- **Ignoring street noise (negative prehension)**:
    - Subject = your current moment of experience
    - Datum = the honk from the street
    - Subjective form = exclusion-from-relevance. The honk is present, but this occasion excludes it from relevance so you can keep reading. That exclusion is still a prehensive act.

- **Choosing words while texting (contrast of forms)**:
    - Subject = your current moment of experience
    - Datum = yesterday’s awkward message
    - Subjective form = avoid-that-tone. You recall yesterday’s awkward message (datum) and feel it as "avoid that tone" (subjective form), shaping today’s reply. Same datum, different form → different outcome.

### Examples to software

In code we model facts and state changes; a "prehension" maps best to one rule-bound uptake of a prior fact by a processing step.

- **Bank transfer posting (policy prehension)**:

    - Subject = the posting step (this processing occasion).
    - Datum = FundsTransferInitiated, current balances, limits.
    - Subjective form = "evaluate for risk/limits; approve or reject."
    The step prehends the facts under its rule and yields a concrete result (posted entries or a rejection).

- **Login audit (redaction prehension)**:

    - Subject = the audit-write step.
    - Datum = LoginSucceeded + user metadata.
    - Subjective form = "mask PII, attach correlation id."
    The logger feels the datum as-to-be-redacted, then commits a record.

- **Orbit integration (step-wise uptake)**:

    - Subject = this integrator step.
    - Datum = current state (x, v), potential parameters, step size policy.
    - Subjective form = "advance with leapfrog; adjust velocity half-kick; (optionally) exclude unstable step."
    Each step prehends the current data via its method and contributes to the finished trajectory.


## The code so far

### Defining the core abstractions
Let's make a stop and try to translate all these thouhgts into functional code. First, let's start with the idea of a `Datum` (a fact that can be felt by an occassion).


```python
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Protocol
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class Datum:
    name: str
    payload: dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str | None = None
    causation_id: str | None = None
```

A few things to note here

- We use `dataclass` to define `Datum`, which makes it easy to create immutable data structures.
- We automatically generate a unique ID and timestamp for each datum instance, but allow them to be overridden if needed.
- Although not necessarily obvious, we introduced `correlation_id` and `causation_id` to help with tracing the flow of data through the system.

Now we want to create our model for an `ActualOccasion`, which will be the core processing unit that can prehend data and produce new data.

```python
@dataclass
class ActualOccasion:
    name: str
    state: dict[str, Any]
    _bindings: list[tuple[DatumSelector, SubjectiveForm]] = field(
        default_factory=lambda: []
    )

    def on(self, selector: DatumSelector, form: SubjectiveForm) -> "ActualOccasion":
        self._bindings.append((selector, form))
        return self

    def handle(self, datum: Datum) -> Iterable[Datum]:
        for selector, form in self._bindings:
            if selector(datum):
                yield from form(self, datum)

```

In plain language, an `ActualOccasion` is a processing step that can take in a `Datum`, do something with it, and produce new `Datum` instances as output. The `handle` method is where the logic for processing the input datum will go.

Final step for now is to define `Prehension`, which represents the act of an occasion feeling a datum.

```python
SubjectiveForm = Callable[[ActualOccasion, Datum], Iterable[Datum]]
DatumSelector  = Callable[[Datum], bool]

@dataclass(frozen=True)
class Prehension:
    subject: ActualOccasion
    selector: DatumSelector
    form: SubjectiveForm
```

Here, a `Prehension` ties together an `ActualOccasion` (the subject), a way to select relevant data (the selector), and a way to process that data (the subjective form).

And that's it for now! We have the basic building blocks to start modeling actual occasions and their prehensions in code.

### Putting it all together
To wire everything together through a simulation, let's consider an domain specific example: a 
payment processing system. First let us define a simple selector

```python
def by_name(name: str) -> DatumSelector:
    def selector(datum: Datum) -> bool:
        return datum.name == name
    return selector
```

This selector will help us filter data by its name. Next, we can define a subjective form that processes a payment:

```python
def consider_payment(payments: ActualOccasion, d: Datum) -> Iterable[Datum]:
    order_id = d.payload["order_id"]
    total = d.payload["total"]
    limit = payments.state.get("limit", 500.0)
    approved = total <= limit
    payments.state.setdefault("decisions", {})[order_id] = {
        "amount": total,
        "approved": approved,
    }
    yield Datum(
        "PaymentAuthorized" if approved else "PaymentDeclined",
        {"order_id": order_id, "amount": total},
        correlation_id=d.correlation_id or d.id,
        causation_id=d.id,
    )
```

This form checks if the payment total is within the allowed limit and yields a new datum indicating whether the payment was authorized or declined.

```python
def record_outcome(decider: ActualOccasion, d: Datum) -> Iterable[Datum]:
    order_id = d.payload["order_id"]
    status = "ACCEPTED" if d.name == "PaymentAuthorized" else "REJECTED"
    decider.state.setdefault("orders", {})[order_id] = {"status": status}
    return ()  # nothing further
```

This form records the final outcome of the payment decision in the occasion's state.

```python
def audit_everything(audit: ActualOccasion, d: Datum) -> Iterable[Datum]:
    audit.state.setdefault("events", []).append((d.name, d.payload))
    return ()
```

This form logs every datum that passes through the audit occasion.

### One final step

So far we have defined our core abstractions and some specific occasions for payment processing. Now we can set up the occasions and simulate some data flowing through them. Let's define a *temporary* method to install the prehensions and run the simulation.

```python
def install(*prehensions: Prehension) -> None:
    """Attach prehensions to their subjects (syntactic sugar)."""
    for ph in prehensions:
        ph.subject.on(ph.selector, ph.form)

def run(initial_data: list[Datum], occasions: list[ActualOccasion]) -> list[Datum]:
    """
    Breadth-first processing loop:
    - Take a datum from the queue
    - Let every occasion handle it (apply its matching prehensions)
    - Enqueue any derived datums
    - Return full closure (inputs + derived)
    """
    queue: list[Datum] = list(initial_data)
    seen: list[Datum] = []
    while queue:
        current = queue.pop(0)
        seen.append(current)
        for occ in occasions:
            derived = list(occ.handle(current))
            queue.extend(derived)
    return seen
```

And with that we are ready to run a simple simulation!

```python
payments = ActualOccasion("Payments", state={"limit": 500.0})
decision = ActualOccasion("OrderDecision")
audit = ActualOccasion("Audit")

# Declare prehensions (then install them)
install(
    Prehension(payments, by_name("OrderPlaced"), consider_payment),
    Prehension(decision, by_name("PaymentAuthorized"), record_outcome),
    Prehension(decision, by_name("PaymentDeclined"), record_outcome),
    Prehension(audit, lambda _d: True, audit_everything),
)

# Seed data
seed = [
    Datum("OrderPlaced", {"order_id": "A-100", "total": 420.0}, id="d1"),
    Datum("OrderPlaced", {"order_id": "B-200", "total": 640.0}, id="d2"),
]

# Run the system 
closure = run(seed, [payments, decision, audit])
```


And to see the results

```python
print("Closure (all data seen):")
for d in closure:
    print(f"  {d.name} {d.payload}")
``` 

Should produce 


```shell
Closure (all datums seen):
  OrderPlaced {'order_id': 'A-100', 'total': 420.0}
  OrderPlaced {'order_id': 'B-200', 'total': 640.0}
  PaymentAuthorized {'order_id': 'A-100', 'amount': 420.0}
  PaymentDeclined {'order_id': 'B-200', 'amount': 640.0}
```

And the final states of the occasions:

```python
print("Payments:", payments.state)
print("Decision:", decision.state)
print("Audit: events_logged =", len(audit.state.get("events", [])))
```

Should produce

```shell
Payments: {'limit': 500.0, 'decisions': {'A-100': {'amount': 420.0, 'approved': True}, 'B-200': {'amount': 640.0, 'approved': False}}}
Decision: {'orders': {'A-100': {'status': 'ACCEPTED'}, 'B-200': {'status': 'REJECTED'}}}
Audit: events_logged = 4
```

## A few concluding remarks

- Occasion owns behavior via `.on(selector, form)`; `handle(datum)` applies the matching prehensions.
- Prehension is first-class: we build them explicitly, then `install(...)` binds them onto their subjects.
- The tiny `run(...)` loop is just glue to push datums around—so you can see everything working before we introduce a bus/router abstraction.
- There is a clear delineation of responsbilities in this framework: who reacts to what and how. Occasions are the subject, prehensions are edges and data are facts. Behavios lives on the dge, by binding a selector and a subjective form to an occasion.
- This framewok suppoers plugin-behvior out of the box, without touching occassion's internal logic. Just add more prehensions to the occassion as needed.
- Unit testability is also improved, since you can test each subjective form in isolation, as a pure function of (occasion, datum) -> derived data.
- Although not complete yet, it is already a embarrassingly parallizable framwerk by design.

