# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import enum
import sys
import typing as t
import warnings

import capellambse.model as m
from capellambse.model import _descriptors, _obj, _pods

from . import behavior, capellacore, modellingcore
from . import namespaces as ns

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

NS = ns.CAPELLACOMMON


@m.stringy_enum
@enum.unique
class ChangeEventKind(enum.Enum):
    WHEN = "WHEN"


@m.stringy_enum
@enum.unique
class TimeEventKind(enum.Enum):
    AT = "AT"
    """Trigger at a specific time.

    An absolute time trigger is specified with the keyword 'at' followed
    by an expression that evaluates to a time value, such as 'Jan. 1,
    2000, Noon'.
    """
    AFTER = "AFTER"
    """Trigger after a relative time duration has passed.

    A relative time trigger is specified with the keyword 'after'
    followed by an expression that evaluates to a time value, such as
    'after (5 seconds)'.
    """


@m.stringy_enum
@enum.unique
class TransitionKind(enum.Enum):
    INTERNAL = "internal"
    LOCAL = "local"
    EXTERNAL = "external"


class AbstractCapabilityPkg(capellacore.Structure, abstract=True):
    pass


class GenericTrace(capellacore.Trace):
    key_value_pairs = _descriptors.Containment["capellacore.KeyValue"](
        "keyValuePairs", (ns.CAPELLACORE, "KeyValue")
    )

    @property
    @deprecated("Synthetic names are deprecated", category=FutureWarning)
    def name(self) -> str:
        myname = type(self).__name__
        if self.target is not None:
            tgname = self.target.name
            tguuid = self.target.uuid
        else:
            tgname = tguuid = "<no target>"
        return f"[{myname}] to {tgname} ({tguuid})"


class TransfoLink(GenericTrace):
    pass


class JustificationLink(GenericTrace):
    pass


class CapabilityRealizationInvolvement(capellacore.Involvement):
    pass


class CapabilityRealizationInvolvedElement(
    capellacore.InvolvedElement, abstract=True
):
    pass


class StateMachine(capellacore.CapellaElement, behavior.AbstractBehavior):
    regions = _descriptors.Containment["Region"]("ownedRegions", (NS, "Region"))
    connection_points = _descriptors.Containment["Pseudostate"](
        "ownedConnectionPoints", (NS, "Pseudostate")
    )


class Region(capellacore.NamedElement):
    _xmltag = "ownedRegions"

    states = _descriptors.Containment["AbstractState"](
        "ownedStates", (NS, "AbstractState")
    )
    transitions = _descriptors.Containment["StateTransition"](
        "ownedTransitions", (NS, "StateTransition")
    )
    involved_states = _descriptors.Association["AbstractState"](
        (NS, "AbstractState"), "involvedStates"
    )

    __modes = _descriptors.Filter["Mode"]("states", (NS, "Mode"))

    @property
    def modes(self) -> _obj.ElementList[Mode]:
        warnings.warn(
            (
                "Region.modes is deprecated, use states instead"
                " (note that states may only contain either States or Modes)"
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        return self.__modes


class AbstractState(
    capellacore.NamedElement, modellingcore.IState, abstract=True
):
    _xmltag = "ownedStates"

    state_realizations = _descriptors.Containment["AbstractStateRealization"](
        "ownedAbstractStateRealizations", (NS, "AbstractStateRealization")
    )
    realized_states = _descriptors.Allocation["AbstractState"](
        "ownedAbstractStateRealizations",
        (NS, "AbstractStateRealization"),
        (NS, "AbstractState"),
        attr="targetElement",
        backattr="sourceElement",
    )
    realizing_states = _descriptors.Backref["AbstractState"](
        (NS, "AbstractState"), "realized_states"
    )
    incoming_transitions = _descriptors.Backref["StateTransition"](
        (NS, "StateTransition"), "target"
    )
    outgoing_transitions = _descriptors.Backref["StateTransition"](
        (NS, "StateTransition"), "source"
    )

    if not t.TYPE_CHECKING:

        @property
        def regions(self) -> _obj.ElementList[Region]:
            myname = AbstractState.__name__
            if type(self) is not AbstractState:
                myname = f"{type(self).__name__}, a subclass of {AbstractState.__name__},"
            warnings.warn(
                (
                    f"{myname} cannot contain regions directly,"
                    f" use the concrete {State.__name__!r} class instead"
                ),
                category=FutureWarning,
                stacklevel=2,
            )
            return _obj.ElementList(self._model, [], Region)


class State(AbstractState):
    """A situation during which some invariant condition holds.

    A condition of a system or element, as defined by some of its
    properties, which can enable system behaviors and/or structure to
    occur.

    Note: The enabled behavior may include no actions, such as
    associated with a wait state. Also, the condition that defines the
    state may be dependent on one or more previous states.
    """

    regions = _descriptors.Containment["Region"]("ownedRegions", (NS, "Region"))
    connection_points = _descriptors.Containment["Pseudostate"](
        "ownedConnectionPoints", (NS, "Pseudostate")
    )
    entry = _descriptors.Association["behavior.AbstractEvent"](
        (ns.BEHAVIOR, "AbstractEvent"), "entry", legacy_by_type=True
    )
    do_activity = _descriptors.Association["behavior.AbstractEvent"](
        (ns.BEHAVIOR, "AbstractEvent"), "doActivity", legacy_by_type=True
    )
    exit = _descriptors.Association["behavior.AbstractEvent"](
        (ns.BEHAVIOR, "AbstractEvent"), "exit", legacy_by_type=True
    )
    state_invariant = _descriptors.Containment["modellingcore.AbstractConstraint"](
        "stateInvariant", (ns.MODELLINGCORE, "AbstractConstraint")
    )
    functions = _descriptors.Backref["fa.AbstractFunction"](
        (ns.FA, "AbstractFunction"), "available_in_states"
    )

    if not t.TYPE_CHECKING:
        entries = _descriptors.DeprecatedAccessor("entry")
        exits = _descriptors.DeprecatedAccessor("exit")


class Mode(State):
    """Characterizes an expected behavior at a point in time.

    A Mode characterizes an expected behaviour through the set of
    functions or elements available at a point in time.
    """


class FinalState(State):
    """Special state signifying that the enclosing region is completed.

    If the enclosing region is directly contained in a state machine and
    all other regions in the state machine also are completed, then it
    means that the entire state machine is completed.
    """


class StateTransition(capellacore.NamedElement, capellacore.Relationship):
    """A directed relationship between a source and target vertex.

    It may be part of a compound transition, which takes the state
    machine from one state configuration to another, representing the
    complete response of the state machine to an occurrence of an event
    of a particular type.
    """

    _xmltag = "ownedTransitions"

    kind = _pods.EnumPOD("kind", TransitionKind)
    trigger_description = _pods.StringPOD("triggerDescription")
    guard = _descriptors.Single["capellacore.Constraint"](
        _descriptors.Association((ns.CAPELLACORE, "Constraint"), "guard")
    )
    source = _descriptors.Single["AbstractState"](
        _descriptors.Association((NS, "AbstractState"), "source")
    )
    target = _descriptors.Single["AbstractState"](
        _descriptors.Association((NS, "AbstractState"), "target")
    )
    effect = _descriptors.Association["behavior.AbstractEvent"](
        (ns.BEHAVIOR, "AbstractEvent"), "effect", legacy_by_type=True
    )
    triggers = _descriptors.Association["behavior.AbstractEvent"](
        (ns.BEHAVIOR, "AbstractEvent"), "triggers", legacy_by_type=True
    )
    state_transition_realizations = _descriptors.Containment[
        "StateTransitionRealization"
    ]("ownedStateTransitionRealizations", (NS, "StateTransitionRealization"))
    realized_transitions = _descriptors.Allocation["StateTransition"](
        "ownedStateTransitionRealizations",
        (NS, "StateTransitionRealization"),
        (NS, "StateTransition"),
        attr="targetElement",
        backattr="sourceElement",
    )

    if not t.TYPE_CHECKING:
        destination = _descriptors.DeprecatedAccessor("target")
        effects = _descriptors.DeprecatedAccessor("effect")


class Pseudostate(AbstractState, abstract=True):
    pass


class InitialPseudoState(Pseudostate):
    pass


class JoinPseudoState(Pseudostate):
    pass


class ForkPseudoState(Pseudostate):
    pass


class ChoicePseudoState(Pseudostate):
    pass


class TerminatePseudoState(Pseudostate):
    pass


class AbstractStateRealization(capellacore.Allocation):
    pass


class StateTransitionRealization(capellacore.Allocation):
    pass


class ShallowHistoryPseudoState(Pseudostate):
    pass


class DeepHistoryPseudoState(Pseudostate):
    pass


class EntryPointPseudoState(Pseudostate):
    pass


class ExitPointPseudoState(Pseudostate):
    pass


class StateEventRealization(capellacore.Allocation):
    pass


class StateEvent(
    capellacore.NamedElement, behavior.AbstractEvent, abstract=True
):
    expression = _descriptors.Association["capellacore.Constraint"](
        (ns.CAPELLACORE, "Constraint"), "expression"
    )
    state_event_realizations = _descriptors.Containment["StateEventRealization"](
        "ownedStateEventRealizations", (NS, "StateEventRealization")
    )
    realized_events = _descriptors.Allocation["StateEvent"](
        "ownedStateEventRealizations",
        (NS, "StateEventRealization"),
        (NS, "StateEvent"),
        attr="targetElement",
        backattr="sourceElement",
    )


class ChangeEvent(StateEvent):
    kind = _pods.EnumPOD("kind", ChangeEventKind)


class TimeEvent(StateEvent):
    kind = _pods.EnumPOD("kind", TimeEventKind)


if not t.TYPE_CHECKING:

    def __getattr__(name):
        if name == "AbstractStateMode":
            warnings.warn(
                "AbstractStateMode has been renamed to AbstractState",
                DeprecationWarning,
                stacklevel=2,
            )
            return AbstractState

        raise AttributeError(name)


from . import fa  # noqa: F401
