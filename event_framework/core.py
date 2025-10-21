"""Core abstractions for an event-driven, process-over-substance framework."""

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class Datum:
    """A fact available to be 'felt' (e.g. a prior occasion's output)."""

    name: str
    payload: dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str | None = None
    causation_id: str | None = None


SubjectiveForm = Callable[["ActualOccasion", Datum], Iterable[Datum]]
DatumSelector = Callable[[Datum], bool]


@dataclass
class ActualOccasion:
    """
    A process node that 'becomes' by taking up (prehending) prior data.

    In DDD terms this can model an aggregate, policy, saga step, projector, etc.
    """

    name: str
    state: dict[str, Any]
    _bindings: list[tuple[DatumSelector, SubjectiveForm]] = field(
        default_factory=lambda: []
    )

    def on(self, selector: DatumSelector, form: SubjectiveForm) -> "ActualOccasion":
        """
        Bind a subjective form to a selector for this occasion.

        Parameters
        ----------
        selector : DatumSelector
            Selector function to match incoming data.
        form : SubjectiveForm
            Subjective form to apply to matching data.

        Returns
        -------
        ActualOccasion
            The occasion itself (for chaining).
        """
        self._bindings.append((selector, form))
        return self

    def handle(self, datum: Datum) -> Iterable[Datum]:
        """
        Handle datum.

        The occasion prehends by running any bound (selector, form) that matches.

        Parameters
        ----------
        datum : Datum
            Datum to prehend.

        Returns
        -------
        Iterable[Datum]
            Derived data emitted by subjective forms.

        Yields
        ------
        Iterator[Iterable[Datum]]
            Derived data emitted by subjective forms.
        """
        for selector, form in self._bindings:
            if selector(datum):
                yield from form(self, datum)


@dataclass(frozen=True)
class Prehension:
    """
    One *directed* way an occasion (subject) 'feels' a prior datum.

    - subject: the occasion doing the prehending (becoming)
    - selector: which data are 'relevant'
    - form: the 'subjective form' — how the subject takes up the datum
    """

    subject: ActualOccasion
    selector: DatumSelector
    form: SubjectiveForm


class Nexus:
    """
    The central event nexus.

    Nexus accepts Datums, lets every Occasion 'feel' them via its
    prehensions, threads correlation/causation, and returns the full closure.
    """

    def __init__(self, name: str):
        """
        Initialize Nexus.

        Parameters
        ----------
        name : str
            Name of the nexus.
        """
        self.name = name
        self._occasions: dict[str, ActualOccasion] = {}
        self._middlewares: list[Callable[[Datum], Datum]] = []

    def add(self, *occasions: ActualOccasion) -> "Nexus":
        """
        Register actual occassions to the nexus.

        Returns
        -------
        Nexus
            The nexus itself (for chaining).
        """
        for occ in occasions:
            self._occasions[occ.name] = occ
        return self

    def bind(self, *prehensions: Prehension) -> "Nexus":
        """
        Register prehensions.

        Returns
        -------
        Nexus
            The nexus itself (for chaining).
        """
        for ph in prehensions:
            ph.subject.on(ph.selector, ph.form)
        return self

    def use(self, middleware: Callable[[Datum], Datum]) -> "Nexus":
        """
        Install a middleware that can annotate/transform each Datum in-flight.

        Parameters
        ----------
        middleware : Callable[[Datum], Datum]
            Middleware function to apply to each datum.

        Returns
        -------
        Nexus
            The nexus itself (for chaining).
        """
        self._middlewares.append(middleware)
        return self

    def _apply_middlewares(self, d: Datum) -> Datum:
        """
        Apply all register middlewares.

        Parameters
        ----------
        d : Datum
            Datum to process.

        Returns
        -------
        Datum
            Datum after all middlewares have been applied.
        """
        for mw in self._middlewares:
            d = mw(d)
        return d

    def emit(self, *data: Datum) -> list[Datum]:
        """
        Push input data and process until quisecence (Breath First Search).

        Returns
        -------
        list[Datum]
            All data emitted, including derived data.
        """
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
        """
        Quick view of each occasion's state for debugging/diagnostics.

        Returns
        -------
        dict[str, dict[str, Any]]
            Mapping of occasion names to their current state.
        """
        return {name: occ.state for name, occ in self._occasions.items()}
