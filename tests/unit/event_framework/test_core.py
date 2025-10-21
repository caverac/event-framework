"""Unit tests for event_framework.core module."""

# pylint: disable=protected-access, unused-argument

from datetime import datetime, timezone
from uuid import UUID

import pytest

from event_framework.core import (
    Datum,
    ActualOccasion,
    Prehension,
    Nexus,
)


class TestDatum:
    """Tests for the Datum class."""

    def test_datum_creation_with_defaults(self):
        """Test creating a Datum with default values."""
        datum = Datum(name="test_event", payload={"key": "value"})

        assert datum.name == "test_event"
        assert datum.payload == {"key": "value"}
        assert isinstance(datum.id, str)
        assert isinstance(UUID(datum.id), UUID)
        assert isinstance(datum.created_at, datetime)
        assert datum.created_at.tzinfo == timezone.utc
        assert datum.correlation_id is None
        assert datum.causation_id is None

    def test_datum_creation_with_all_fields(self):
        """Test creating a Datum with all fields specified."""
        created_time = datetime.now(timezone.utc)
        datum = Datum(
            name="custom_event",
            payload={"data": 123},
            id="custom-id",
            created_at=created_time,
            correlation_id="corr-123",
            causation_id="cause-456",
        )

        assert datum.name == "custom_event"
        assert datum.payload == {"data": 123}
        assert datum.id == "custom-id"
        assert datum.created_at == created_time
        assert datum.correlation_id == "corr-123"
        assert datum.causation_id == "cause-456"

    def test_datum_immutability(self):
        """Test that Datum is immutable (frozen dataclass)."""
        datum = Datum(name="test", payload={})

        with pytest.raises(AttributeError):
            datum.name = "new_name"  # type: ignore

        with pytest.raises(AttributeError):
            datum.payload = {"new": "payload"}  # type: ignore


class TestActualOccasion:
    """Tests for the ActualOccasion class."""

    def test_occasion_creation(self):
        """Test creating an ActualOccasion."""
        occasion = ActualOccasion(name="test_occasion", state={"count": 0})

        assert occasion.name == "test_occasion"
        assert occasion.state == {"count": 0}
        assert not occasion._bindings  # type: ignore[arg-type]

    def test_on_method_returns_self(self):
        """Test that the on method returns self for chaining."""
        occasion = ActualOccasion(name="test", state={})

        def selector(d: Datum):
            return True

        def form(occ: ActualOccasion, d: Datum) -> list[Datum]:
            return []

        result = occasion.on(selector, form)

        assert result is occasion
        assert len(occasion._bindings) == 1  # type: ignore[arg-type]
        assert occasion._bindings[0] == (selector, form)  # type: ignore[arg-type]

    def test_handle_no_matching_selectors(self):
        """Test handle when no selectors match the datum."""
        occasion = ActualOccasion(name="test", state={})

        def selector(d: Datum):
            return d.name == "other_event"

        def form(occ: ActualOccasion, d: Datum):
            return [Datum(name="output", payload={})]

        occasion.on(selector, form)
        datum = Datum(name="test_event", payload={})

        result = list(occasion.handle(datum))

        assert not result

    def test_handle_single_matching_selector(self):
        """Test handle with a single matching selector."""
        occasion = ActualOccasion(name="test", state={"counter": 0})

        def increment_form(occ: ActualOccasion, d: Datum) -> list[Datum]:
            occ.state["counter"] += 1
            return [
                Datum(name="incremented", payload={"new_count": occ.state["counter"]})
            ]

        def selector(d: Datum) -> bool:
            return d.name == "increment"

        occasion.on(selector, increment_form)

        datum = Datum(name="increment", payload={})
        result = list(occasion.handle(datum))

        assert len(result) == 1
        assert result[0].name == "incremented"
        assert result[0].payload == {"new_count": 1}
        assert occasion.state["counter"] == 1

    def test_handle_multiple_matching_selectors(self):
        """Test handle with multiple matching selectors."""
        occasion = ActualOccasion(name="test", state={})

        def form1(occ: ActualOccasion, d: Datum) -> list[Datum]:
            return [Datum(name="output1", payload={"from": "form1"})]

        def form2(occ: ActualOccasion, d: Datum) -> list[Datum]:
            return [Datum(name="output2", payload={"from": "form2"})]

        def selector1(d: Datum) -> bool:
            return True  # Always matches

        def selector2(d: Datum) -> bool:
            return True  # Always matches

        occasion.on(selector1, form1).on(selector2, form2)

        datum = Datum(name="test", payload={})
        result = list(occasion.handle(datum))

        assert len(result) == 2
        assert result[0].name == "output1"
        assert result[1].name == "output2"

    def test_handle_form_returns_multiple_data(self):
        """Test handle when a form returns multiple data items."""
        occasion = ActualOccasion(name="test", state={})

        def multi_form(occ: ActualOccasion, d: Datum) -> list[Datum]:
            return [
                Datum(name="output1", payload={"index": 1}),
                Datum(name="output2", payload={"index": 2}),
                Datum(name="output3", payload={"index": 3}),
            ]

        def selector(d: Datum) -> bool:
            return True

        occasion.on(selector, multi_form)

        datum = Datum(name="test", payload={})
        result = list(occasion.handle(datum))

        assert len(result) == 3
        assert all(r.name.startswith("output") for r in result)


class TestPrehension:
    """Tests for the Prehension class."""

    def test_prehension_creation(self):
        """Test creating a Prehension."""
        occasion = ActualOccasion(name="test", state={})

        def selector(d: Datum) -> bool:
            return True

        def form(occ: ActualOccasion, d: Datum) -> list[Datum]:
            return []

        prehension = Prehension(subject=occasion, selector=selector, form=form)

        assert prehension.subject is occasion
        assert prehension.selector is selector
        assert prehension.form is form

    def test_prehension_immutability(self):
        """Test that Prehension is immutable."""
        occasion = ActualOccasion(name="test", state={})

        def selector(d: Datum) -> bool:
            return True

        def form(occ: ActualOccasion, d: Datum) -> list[Datum]:
            return []

        prehension = Prehension(subject=occasion, selector=selector, form=form)

        with pytest.raises(AttributeError):
            prehension.subject = ActualOccasion(name="other", state={})  # type: ignore


class TestNexus:
    """Tests for the Nexus class."""

    def test_nexus_creation(self):
        """Test creating a Nexus."""
        nexus = Nexus(name="test_nexus")

        assert nexus.name == "test_nexus"
        assert not nexus._occasions  # type: ignore[attr-defined]
        assert not nexus._middlewares  # type: ignore[attr-defined]

    def test_add_single_occasion(self):
        """Test adding a single occasion to the nexus."""
        nexus = Nexus(name="test")
        occasion = ActualOccasion(name="occ1", state={})

        result = nexus.add(occasion)

        assert result is nexus  # Returns self for chaining
        assert "occ1" in nexus._occasions  # type: ignore[attr-defined]
        assert nexus._occasions["occ1"] is occasion  # type: ignore[attr-defined]

    def test_add_multiple_occasions(self):
        """Test adding multiple occasions to the nexus."""
        nexus = Nexus(name="test")
        occ1 = ActualOccasion(name="occ1", state={})
        occ2 = ActualOccasion(name="occ2", state={})

        nexus.add(occ1, occ2)

        assert len(nexus._occasions) == 2  # type: ignore[attr-defined]
        assert nexus._occasions["occ1"] is occ1  # type: ignore[attr-defined]
        assert nexus._occasions["occ2"] is occ2  # type: ignore[attr-defined]

    def test_bind_prehensions(self):
        """Test binding prehensions to the nexus."""
        nexus = Nexus(name="test")
        occasion = ActualOccasion(name="occ", state={})

        def selector(d: Datum) -> bool:
            return True

        def form(occ: ActualOccasion, d: Datum) -> list[Datum]:
            return []

        prehension = Prehension(subject=occasion, selector=selector, form=form)

        result = nexus.bind(prehension)

        assert result is nexus  # Returns self for chaining
        assert len(occasion._bindings) == 1  # type: ignore[arg-type]
        assert occasion._bindings[0] == (selector, form)  # type: ignore[arg-type]

    def test_use_middleware(self):
        """Test adding middleware to the nexus."""
        nexus = Nexus(name="test")

        def middleware(datum: Datum) -> Datum:
            return Datum(
                name=datum.name,
                payload={**datum.payload, "middleware": "applied"},
                id=datum.id,
                created_at=datum.created_at,
                correlation_id=datum.correlation_id,
                causation_id=datum.causation_id,
            )

        result = nexus.use(middleware)

        assert result is nexus  # Returns self for chaining
        assert len(nexus._middlewares) == 1  # type: ignore[attr-defined]
        assert nexus._middlewares[0] is middleware  # type: ignore[attr-defined]

    def test_apply_middlewares(self):
        """Test applying middlewares to a datum."""
        nexus = Nexus(name="test")

        def add_timestamp(datum: Datum) -> Datum:
            return Datum(
                name=datum.name,
                payload={**datum.payload, "processed_at": "2001-01-01"},
                id=datum.id,
                created_at=datum.created_at,
                correlation_id=datum.correlation_id,
                causation_id=datum.causation_id,
            )

        def add_version(datum: Datum) -> Datum:
            return Datum(
                name=datum.name,
                payload={**datum.payload, "version": "1.0"},
                id=datum.id,
                created_at=datum.created_at,
                correlation_id=datum.correlation_id,
                causation_id=datum.causation_id,
            )

        nexus.use(add_timestamp).use(add_version)

        original = Datum(name="test", payload={"data": "value"})
        result = nexus._apply_middlewares(original)  # type: ignore[attr-defined]

        assert result.name == "test"
        assert result.payload["data"] == "value"
        assert result.payload["processed_at"] == "2001-01-01"
        assert result.payload["version"] == "1.0"

    def test_emit_simple_case(self):
        """Test emit with a simple case (no derived data)."""
        nexus = Nexus(name="test")
        occasion = ActualOccasion(name="occ", state={})

        # Selector that never matches
        def selector(d: Datum) -> bool:
            return False

        def form(occ: ActualOccasion, d: Datum) -> list[Datum]:
            return []

        occasion.on(selector, form)

        nexus.add(occasion)

        datum = Datum(name="test", payload={"key": "value"})
        result = nexus.emit(datum)

        assert len(result) == 1
        assert result[0] is datum

    # def test_emit_with_derived_data(self):
    #     """Test emit with occasions that generate derived data."""
    #     nexus = Nexus(name="test")
    #     occasion = ActualOccasion(name="occ", state={})

    #     def create_derived(occ: ActualOccasion, d: Datum) -> list[Datum]:
    #         if d.name == "input":
    #             return [Datum(name="derived", payload={"source": d.name})]
    #         return []

    #     def selector(d: Datum) -> bool:
    #         return d.name == "input"

    #     occasion.on(selector, create_derived)
    #     nexus.add(occasion)

    #     input_datum = Datum(name="input", payload={"data": "test"})
    #     result = nexus.emit(input_datum)

    #     assert len(result) == 2
    #     assert result[0].name == "input"
    #     assert result[1].name == "derived"
    #     assert result[1].correlation_id == input_datum.id
    #     assert result[1].causation_id == input_datum.id

    # def test_emit_with_chain_reaction(self):
    #     """Test emit with a chain reaction of derived data."""
    #     nexus = Nexus(name="test")

    #     # First occasion: input -> intermediate
    #     occ1 = ActualOccasion(name="occ1", state={})

    #     def input_selector(d: Datum) -> bool:
    #         return d.name == "input"

    #     def input_form(occ: ActualOccasion, d: Datum) -> list[Datum]:
    #         return [Datum(name="intermediate", payload={"step": 1})]

    #     occ1.on(input_selector, input_form)

    #     # Second occasion: intermediate -> final
    #     occ2 = ActualOccasion(name="occ2", state={})

    #     def intermediate_selector(d: Datum) -> bool:
    #         return d.name == "intermediate"

    #     def intermediate_form(occ: ActualOccasion, d: Datum) -> list[Datum]:
    #         return [Datum(name="final", payload={"step": 2})]

    #     occ2.on(intermediate_selector, intermediate_form)

    #     nexus.add(occ1, occ2)

    #     input_datum = Datum(name="input", payload={})
    #     result = nexus.emit(input_datum)

    #     assert len(result) == 3
    #     assert result[0].name == "input"
    #     assert result[1].name == "intermediate"
    #     assert result[2].name == "final"

    #     # Check causation chain
    #     assert result[1].correlation_id == input_datum.id
    #     assert result[1].causation_id == input_datum.id
    #     assert result[2].correlation_id == input_datum.id  # Same correlation
    #     assert result[2].causation_id == result[1].id  # Caused by intermediate

    # def test_emit_multiple_input_data(self):
    #     """Test emit with multiple input data items."""
    #     nexus = Nexus(name="test")
    #     occasion = ActualOccasion(name="occ", state={})

    #     # Echo each datum
    #     def echo_selector(d: Datum) -> bool:
    #         return True

    #     def echo_form(occ: ActualOccasion, d: Datum) -> list[Datum]:
    #         return [Datum(name=f"echo_{d.name}", payload=d.payload)]

    #     occasion.on(echo_selector, echo_form)

    #     nexus.add(occasion)

    #     datum1 = Datum(name="first", payload={"id": 1})
    #     datum2 = Datum(name="second", payload={"id": 2})

    #     result = nexus.emit(datum1, datum2)

    #     assert len(result) == 4
    #     input_names = {r.name for r in result if not r.name.startswith("echo_")}
    #     echo_names = {r.name for r in result if r.name.startswith("echo_")}

    #     assert input_names == {"first", "second"}
    #     assert echo_names == {"echo_first", "echo_second"}

    # def test_emit_with_middleware(self):
    #     """Test emit with middleware applied."""
    #     nexus = Nexus(name="test")

    #     # Middleware that adds a timestamp
    #     def timestamp_middleware(datum: Datum) -> Datum:
    #         return Datum(
    #             name=datum.name,
    #             payload={**datum.payload, "timestamp": "2001-01-01"},
    #             id=datum.id,
    #             created_at=datum.created_at,
    #             correlation_id=datum.correlation_id,
    #             causation_id=datum.causation_id,
    #         )

    #     nexus.use(timestamp_middleware)

    #     datum = Datum(name="test", payload={"data": "value"})
    #     result = nexus.emit(datum)

    #     assert len(result) == 1
    #     assert result[0].payload["timestamp"] == "2001-01-01"

    # def test_snapshot(self):
    #     """Test taking a snapshot of occasion states."""
    #     nexus = Nexus(name="test")

    #     occ1 = ActualOccasion(name="counter", state={"count": 5})
    #     occ2 = ActualOccasion(name="accumulator", state={"total": 100, "items": 10})

    #     nexus.add(occ1, occ2)

    #     snapshot = nexus.snapshot()

    #     expected = {"counter": {"count": 5}, "accumulator": {"total": 100, "items": 10}}

    #     assert snapshot == expected

    # def test_snapshot_empty_nexus(self):
    #     """Test snapshot with no occasions."""
    #     nexus = Nexus(name="empty")
    #     snapshot = nexus.snapshot()
    #     assert not snapshot


# class TestIntegration:
#     """Integration tests combining multiple components."""

#     def test_event_sourced_counter(self):
#         """Test a simple event-sourced counter using the framework."""
#         nexus = Nexus(name="counter_system")

#         # Counter aggregate
#         counter = ActualOccasion(name="counter", state={"value": 0})

#         def handle_increment(occ, datum):
#             amount = datum.payload.get("amount", 1)
#             occ.state["value"] += amount
#             return [
#                 Datum(
#                     name="counter_incremented",
#                     payload={"new_value": occ.state["value"], "amount": amount},
#                 )
#             ]

#         def handle_decrement(occ, datum):
#             amount = datum.payload.get("amount", 1)
#             occ.state["value"] -= amount
#             return [
#                 Datum(
#                     name="counter_decremented",
#                     payload={"new_value": occ.state["value"], "amount": amount},
#                 )
#             ]

#         def increment_selector(d):
#             return d.name == "increment"

#         def decrement_selector(d):
#             return d.name == "decrement"

#         counter.on(increment_selector, handle_increment)
#         counter.on(decrement_selector, handle_decrement)

#         # Projection
#         projection = ActualOccasion(name="counter_projection", state={"history": []})

#         def record_change(occ, datum):
#             if datum.name in ["counter_incremented", "counter_decremented"]:
#                 occ.state["history"].append(
#                     {
#                         "event": datum.name,
#                         "value": datum.payload["new_value"],
#                         "timestamp": datum.created_at.isoformat(),
#                     }
#                 )
#             return []

#         def all_selector(d):
#             return True

#         projection.on(all_selector, record_change)

#         nexus.add(counter, projection)

#         # Execute commands
#         events = nexus.emit(
#             Datum(name="increment", payload={"amount": 5}),
#             Datum(name="increment", payload={"amount": 3}),
#             Datum(name="decrement", payload={"amount": 2}),
#         )

#         # Verify final state
#         assert counter.state["value"] == 6  # 0 + 5 + 3 - 2
#         assert len(projection.state["history"]) == 3

#         # Verify event chain
#         event_names = [e.name for e in events]
#         assert "increment" in event_names
#         assert "counter_incremented" in event_names
#         assert "counter_decremented" in event_names

#     def test_saga_pattern(self):
#         """Test implementing a saga pattern with the framework."""
#         nexus = Nexus(name="order_saga")

#         # Order saga
#         saga = ActualOccasion(name="order_saga", state={"orders": {}})

#         def start_order(occ, datum):
#             order_id = datum.payload["order_id"]
#             occ.state["orders"][order_id] = {"status": "payment_pending"}
#             return [Datum(name="payment_requested", payload={"order_id": order_id})]

#         def handle_payment_success(occ, datum):
#             order_id = datum.payload["order_id"]
#             if order_id in occ.state["orders"]:
#                 occ.state["orders"][order_id]["status"] = "inventory_pending"
#                 return [
#                     Datum(name="inventory_reserved", payload={"order_id": order_id})
#                 ]
#             return []

#         def handle_inventory_success(occ, datum):
#             order_id = datum.payload["order_id"]
#             if order_id in occ.state["orders"]:
#                 occ.state["orders"][order_id]["status"] = "completed"
#                 return [Datum(name="order_completed", payload={"order_id": order_id})]
#             return []

#         def order_created_selector(d):
#             return d.name == "order_created"

#         def payment_succeeded_selector(d):
#             return d.name == "payment_succeeded"

#         def inventory_reserved_selector(d):
#             return d.name == "inventory_reserved"

#         saga.on(order_created_selector, start_order)
#         saga.on(payment_succeeded_selector, handle_payment_success)
#         saga.on(inventory_reserved_selector, handle_inventory_success)

#         nexus.add(saga)

#         # Simulate order flow
#         events = nexus.emit(
#             Datum(name="order_created", payload={"order_id": "order-123"}),
#             Datum(name="payment_succeeded", payload={"order_id": "order-123"}),
#         )

#         # Verify saga state progression
#         order_state = saga.state["orders"]["order-123"]
#         assert order_state["status"] == "completed"

#         # Verify event chain
#         event_names = [e.name for e in events]
#         assert "order_created" in event_names
#         assert "payment_requested" in event_names
#         assert "inventory_reserved" in event_names
#         assert "order_completed" in event_names
