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

    def test_emit_with_derived_data(self):
        """Test emit with occasions that generate derived data."""
        nexus = Nexus(name="test")
        occasion = ActualOccasion(name="occ", state={})

        def create_derived(occ: ActualOccasion, d: Datum) -> list[Datum]:
            if d.name == "input":
                return [Datum(name="derived", payload={"source": d.name})]
            return []

        def selector(d: Datum) -> bool:
            return d.name == "input"

        occasion.on(selector, create_derived)
        nexus.add(occasion)

        input_datum = Datum(name="input", payload={"data": "test"})
        result = nexus.emit(input_datum)

        assert len(result) == 2
        assert result[0].name == "input"
        assert result[1].name == "derived"
        assert result[1].correlation_id == input_datum.id
        assert result[1].causation_id == input_datum.id

    def test_emit_with_chain_reaction(self):
        """Test emit with a chain reaction of derived data."""
        nexus = Nexus(name="test")

        # First occasion: input -> intermediate
        occ1 = ActualOccasion(name="occ1", state={})

        def input_selector(d: Datum) -> bool:
            return d.name == "input"

        def input_form(occ: ActualOccasion, d: Datum) -> list[Datum]:
            return [Datum(name="intermediate", payload={"step": 1})]

        occ1.on(input_selector, input_form)

        # Second occasion: intermediate -> final
        occ2 = ActualOccasion(name="occ2", state={})

        def intermediate_selector(d: Datum) -> bool:
            return d.name == "intermediate"

        def intermediate_form(occ: ActualOccasion, d: Datum) -> list[Datum]:
            return [Datum(name="final", payload={"step": 2})]

        occ2.on(intermediate_selector, intermediate_form)

        nexus.add(occ1, occ2)

        input_datum = Datum(name="input", payload={})
        result = nexus.emit(input_datum)

        assert len(result) == 3
        assert result[0].name == "input"
        assert result[1].name == "intermediate"
        assert result[2].name == "final"

        # Check causation chain
        assert result[1].correlation_id == input_datum.id
        assert result[1].causation_id == input_datum.id
        assert result[2].correlation_id == input_datum.id  # Same correlation
        assert result[2].causation_id == result[1].id  # Caused by intermediate

    def test_emit_with_middleware(self):
        """Test emit with middleware applied."""
        nexus = Nexus(name="test")

        # Middleware that adds a timestamp
        def timestamp_middleware(datum: Datum) -> Datum:
            return Datum(
                name=datum.name,
                payload={**datum.payload, "timestamp": "2001-01-01"},
                id=datum.id,
                created_at=datum.created_at,
                correlation_id=datum.correlation_id,
                causation_id=datum.causation_id,
            )

        nexus.use(timestamp_middleware)

        datum = Datum(name="test", payload={"data": "value"})
        result = nexus.emit(datum)

        assert len(result) == 1
        assert result[0].payload["timestamp"] == "2001-01-01"

    def test_snapshot(self):
        """Test taking a snapshot of occasion states."""
        nexus = Nexus(name="test")

        occ1 = ActualOccasion(name="counter", state={"count": 5})
        occ2 = ActualOccasion(name="accumulator", state={"total": 100, "items": 10})

        nexus.add(occ1, occ2)

        snapshot = nexus.snapshot()

        expected = {"counter": {"count": 5}, "accumulator": {"total": 100, "items": 10}}

        assert snapshot == expected

    def test_snapshot_empty_nexus(self):
        """Test snapshot with no occasions."""
        nexus = Nexus(name="empty")
        snapshot = nexus.snapshot()
        assert not snapshot
