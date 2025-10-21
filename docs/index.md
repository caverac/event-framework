# Event Framework

Welcome to the documentation for the Event Framework, a Whitehead-inspired Domain-Driven Design framework — *"From Philosophical Cosmology to Software Design."*


Traditionally software frameworks start from things (entities, tables, classes). This project starts from **change** -- how facts become decisions and decisions become new facts. That perspective comes from Alfred North Whitehead's "process" view of reality [@whitehead1929], and it maps surprisingly cleanly onto Domain-Driven Design (DDD) once we translate the terms [@evans2004]. Importantly, this 
is not to say that directly applying Whitehead's metaphysics to software will explicitly solve
all the intricate problems of software design. Rather, by adopting a process-oriented view of software design, we can rediscover and clarify DDD concepts.

Here's the promise: if you model software the way Whitehead models reality-as a series of small, concrete decision-events—you end up rediscovering DDD patterns. This documention will guide you through the core ideas, concepts, and practical usage of the Event Framework starting from the philosophical foundations to hands-on examples.

## The core idea in plain language

- **Reality as steps, not snapshots.**
Instead of asking "what is the system?" we ask "what just happened to the system, and what does it cause next?" Each step is a tiny occasion (a decision point) that reads what's relevant, applies rules, and produces an outcome.

- **Every decision "grabs" only what matters.**
An occasion prehends (grabs) just the facts and inputs it needs: current balance, an incoming amount, today's policy. This is like a use case gathering its dependencies and context—explicit, testable, and minimal.

- **Rules are types you can reuse.**
What Whitehead calls eternal objects we treat as invariants (typed constraints/value objects): "amount > 0.01", "user is verified", "orbit step > max dt". You pass them into the decision so validation is visible, versionable, and easy to swap.

- **Many inputs → one committed result.**
The decision process (concrescence) takes those facts + rules and resolves them into exactly one satisfaction: a new state and the events that follow. In code: `return {state, events}`.

- **Outcomes are first-class events.**
The externally visible result (superject) is an event you can publish: `deposit_recorded`, `order_shipped`, `orbit_integrated`. That's just DDD's domain events—with an explicit "how we got here" story.

## Why this helps a software engineer

- **Clear boundaries.**
Each occasion is a small, single-purpose decision. It's easier to test, reason about, and compose than a grab-bag "service" method.

- **Traceable logic.**
Because an occasion declares what it reads (prehensions) and what rules it uses (invariants), you can audit decisions: which inputs and constraints produced this event?

- **Safer change.**
Moving a policy from "hardcoded if" to an explicit invariant means you can version policies, AB-test them, or swap them per tenant without touching the core decision logic.

- **Natural fit with DDD.**

    - Occasion ≈ application service / domain use case
    - Prehension ≈ explicit inputs + loaded facts
    - Concrescence ≈ domain logic that derives one outcome
    - Invariants (eternal objects) ≈ value objects / policies / guards
    - Satisfaction ≈ committed aggregate state
    - Superject (event) ≈ domain event for other bounded contexts

## A 30-second example

### Scenario
We need to accept deposits into an account while enforcing business rules (minimum amount, daily limits, KYC status), and we want a clear audit trail of how each balance change was decided.

### What problem are we trying to solve?
- Update an account's balance safely under explicit rules (policy may change per tenant/region).
- Make each balance change auditable: which facts and rules produced it?
- Keep logic testable and composable (e.g., reuse the same rules for ACH, card, promo credits).

### The process
- **Inputs:** `balance = 100.00`, `amount = 25.00`.
- **Invariants:** `amount > 0.01`.
- The **occasion** "Deposit" prehends `balance` and `amount`.
- It **concresces** by checking invariants and computing `new_balance = 125.00`.
- **Satisfaction:** `{state: balance = 125.00, events: [deposit_recorded(25.00)]}`.
- Other contexts react to the event (notifications, ledger, limits).

### Why the proposed approach works
We model the change as a single Occasion (decision step). It explicitly:

- Prehends only the relevant facts/inputs (current balance, amount, user flags).
- Applies Invariants (typed rules/policies) during Concrescence to yield exactly one Decision: {state, events}.
- Emits a domain event as the externally visible outcome (for ledgers, notifications, limits).

No philosophy degree needed. Just a shift in modeling: treat every meaningful change as a small, explicit decision with declared inputs, rules, and one outcome. Do that consistently, and the usual DDD structures fall into place—only now they're motivated by a simple mental model you can explain to anyone.

### Why is it better than a "regular class with one method that updates state?"

- **Traceability**: You can answer "why did balance change?" by inspecting prehension + invariants. A single "update_balance(amount)" often buries this context in ad-hoc conditionals.

- **Policy agility**: Rules live in Invariants, not hardcoded ifs. You can version/swap them (per region/tenant/AB test) without rewriting the decision code.

- **Safety & testing**: The decision returns {state, events} in a pure function style; you can unit-test it with no I/O, then wire persistence/event buses separately.

- **Composability**: Different occasions can reuse the same invariants (e.g., MinAmount, NotFrozen, DailyLimit) or combine them.

## Here we go!
No philosophy degree needed. Just a shift in modeling: treat every meaningful change as a small, explicit decision with declared inputs, rules, and one outcome. Do that consistently, and the usual DDD structures fall into place—only now they're motivated by a simple mental model you can explain to anyone.

## References
\bibliography