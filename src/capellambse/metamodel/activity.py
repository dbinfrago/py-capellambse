# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import enum

import capellambse.model as m
from capellambse.metamodel.behavior import AbstractBehavior, AbstractSignal
from capellambse.model import _descriptors, _pods

from . import modellingcore
from . import namespaces as ns

NS = ns.ACTIVITY


@m.stringy_enum
@enum.unique
class ObjectNodeKind(enum.Enum):
    """The behavior type of the object node with respect to incoming data."""

    UNSPECIFIED = "Unspecified"
    """Used when incoming object node management policy is not specified."""
    NO_BUFFER = "NoBuffer"
    """Discard incoming tokens if they are refused.

    When the "nobuffer" stereotype is applied to object nodes, tokens
    arriving at the node are discarded if they are refused by outgoing
    edges, or refused by actions for object nodes that are input pins.
    """
    OVERWRITE = "Overwrite"
    """Incoming tokens may overwrite existing ones.

    When the "overwrite" stereotype is applied to object nodes, a token
    arriving at a full object node replaces the ones already there. A
    full object node has as many tokens as allowed by its upper bound.
    """


@m.stringy_enum
@enum.unique
class ObjectNodeOrderingKind(enum.Enum):
    """Indicates queuing order within a node."""

    FIFO = "FIFO"
    """First In First Out ordering."""
    LIFO = "LIFO"
    """Last In First Out ordering."""
    ORDERED = "ordered"
    """Indicates that object node tokens are ordered."""
    UNORDERED = "unordered"
    """Indicates that object node tokens are unordered."""


class AbstractActivity(
    AbstractBehavior, modellingcore.TraceableElement, abstract=True
):
    is_read_only = _pods.BoolPOD("isReadOnly")
    is_single_execution = _pods.BoolPOD("isSingleExecution")
    nodes = _descriptors.Containment["ActivityNode"]("ownedNodes", (NS, "ActivityNode"))
    edges = _descriptors.Containment["ActivityEdge"]("ownedEdges", (NS, "ActivityEdge"))
    groups = _descriptors.Containment["ActivityGroup"](
        "ownedGroups", (NS, "ActivityGroup")
    )


class ExceptionHandler(modellingcore.ModelElement, abstract=True):
    protected_node = _descriptors.Single["ExecutableNode"](
        _descriptors.Association((NS, "ExecutableNode"), "protectedNode")
    )
    handler_body = _descriptors.Single["ExecutableNode"](
        _descriptors.Association((NS, "ExecutableNode"), "handlerBody")
    )
    exception_input = _descriptors.Single["ObjectNode"](
        _descriptors.Association((NS, "ObjectNode"), "exceptionInput")
    )
    exception_types = _descriptors.Association["modellingcore.AbstractType"](
        (ns.MODELLINGCORE, "AbstractType"), "exceptionTypes"
    )


class ActivityGroup(modellingcore.ModelElement, abstract=True):
    super_group = _descriptors.Association["ActivityGroup"](
        (NS, "ActivityGroup"), "superGroup"
    )
    sub_groups = _descriptors.Containment["ActivityGroup"](
        "subGroups", (NS, "ActivityGroup")
    )
    nodes = _descriptors.Containment["ActivityNode"]("ownedNodes", (NS, "ActivityNode"))
    edges = _descriptors.Containment["ActivityEdge"]("ownedEdges", (NS, "ActivityEdge"))


class InterruptibleActivityRegion(ActivityGroup, abstract=True):
    interrupting_edges = _descriptors.Association["ActivityEdge"](
        (NS, "ActivityEdge"), "interruptingEdges"
    )


class ActivityEdge(modellingcore.AbstractRelationship, abstract=True):
    rate_kind = _pods.EnumPOD("kindOfRate", modellingcore.RateKind)
    rate = _descriptors.Containment["modellingcore.ValueSpecification"](
        "rate", (ns.MODELLINGCORE, "ValueSpecification")
    )
    probability = _descriptors.Containment["modellingcore.ValueSpecification"](
        "probability", (ns.MODELLINGCORE, "ValueSpecification")
    )
    target = _descriptors.Single["ActivityNode"](
        _descriptors.Association((NS, "ActivityNode"), "target")
    )
    source = _descriptors.Single["ActivityNode"](
        _descriptors.Association((NS, "ActivityNode"), "source")
    )
    guard = _descriptors.Containment["modellingcore.ValueSpecification"](
        "guard", (ns.MODELLINGCORE, "ValueSpecification")
    )
    weight = _descriptors.Containment["modellingcore.ValueSpecification"](
        "weight", (ns.MODELLINGCORE, "ValueSpecification")
    )
    interrupts = _descriptors.Association["InterruptibleActivityRegion"](
        (NS, "InterruptibleActivityRegion"), "interrupts"
    )


class ControlFlow(ActivityEdge, abstract=True):
    """An edge that starts an activity node after the previous one finished."""


class ObjectFlow(ActivityEdge, abstract=True):
    """Models the flow of values to or from object nodes."""

    is_multicast = _pods.BoolPOD("isMulticast")
    is_multireceive = _pods.BoolPOD("isMultireceive")
    transformation = _descriptors.Single[AbstractBehavior](
        _descriptors.Association((ns.BEHAVIOR, "AbstractBehavior"), "transformation")
    )
    selection = _descriptors.Single[AbstractBehavior](
        _descriptors.Association((ns.BEHAVIOR, "AbstractBehavior"), "selection")
    )


class ActivityPartition(
    ActivityGroup, modellingcore.AbstractNamedElement, abstract=True
):
    is_dimension = _pods.BoolPOD("isDimension")
    is_external = _pods.BoolPOD("isExternal")
    represented_element = _descriptors.Single["modellingcore.AbstractType"](
        _descriptors.Association((ns.MODELLINGCORE, "AbstractType"), "representedElement")
    )


class ActivityExchange(modellingcore.AbstractInformationFlow, abstract=True):
    pass


class ActivityNode(modellingcore.AbstractNamedElement, abstract=True):
    pass


class ExecutableNode(ActivityNode, abstract=True):
    handlers = _descriptors.Containment["ExceptionHandler"](
        "ownedHandlers", (NS, "ExceptionHandler")
    )


class AbstractAction(
    ExecutableNode, modellingcore.AbstractNamedElement, abstract=True
):
    local_precondition = _descriptors.Single["modellingcore.AbstractConstraint"](
        _descriptors.Containment(
            "localPrecondition", (ns.MODELLINGCORE, "AbstractConstraint")
        )
    )
    local_postcondition = _descriptors.Single["modellingcore.AbstractConstraint"](
        _descriptors.Containment(
            "localPostcondition", (ns.MODELLINGCORE, "AbstractConstraint")
        )
    )
    context = _descriptors.Association["modellingcore.AbstractType"](
        (ns.MODELLINGCORE, "AbstractType"), "context"
    )
    inputs = _descriptors.Containment["InputPin"]("inputs", (NS, "InputPin"))
    outputs = _descriptors.Containment["OutputPin"]("outputs", (NS, "OutputPin"))


class StructuredActivityNode(ActivityGroup, AbstractAction, abstract=True):
    pass


class AcceptEventAction(AbstractAction, abstract=True):
    is_unmarshall = _pods.BoolPOD("isUnmarshall")
    result = _descriptors.Containment["OutputPin"]("result", (NS, "OutputPin"))


class InvocationAction(AbstractAction, abstract=True):
    arguments = _descriptors.Containment["InputPin"]("arguments", (NS, "InputPin"))


class SendSignalAction(InvocationAction, abstract=True):
    target = _descriptors.Single["InputPin"](_descriptors.Containment("target", (NS, "InputPin")))
    signal = _descriptors.Single[AbstractSignal](
        _descriptors.Association((ns.BEHAVIOR, "AbstractSignal"), "signal")
    )

class CallAction(InvocationAction, abstract=True):
    results = _descriptors.Containment["OutputPin"]("results", (NS, "OutputPin"))

class CallBehaviorAction(CallAction, abstract=True):
    behavior = _descriptors.Single[AbstractBehavior](
        _descriptors.Association((ns.BEHAVIOR, "AbstractBehavior"), "behavior")
    )


class ObjectNode(
    ActivityNode, modellingcore.AbstractTypedElement, abstract=True
):
    is_control_type = _pods.BoolPOD("isControlType")
    node_kind = _pods.EnumPOD("kindOfNode", ObjectNodeKind)
    ordering = _pods.EnumPOD("ordering", ObjectNodeOrderingKind)
    upper_bound = _descriptors.Containment["modellingcore.ValueSpecification"](
        "upperBound", (ns.MODELLINGCORE, "ValueSpecification")
    )
    in_state = _descriptors.Association["modellingcore.IState"](
        (ns.MODELLINGCORE, "IState"), "inState"
    )
    selection = _descriptors.Single[AbstractBehavior](
        _descriptors.Association((ns.BEHAVIOR, "AbstractBehavior"), "selection")
    )


class Pin(ObjectNode, abstract=True):
    is_control = _pods.BoolPOD("isControl")


class InputPin(Pin, abstract=True):
    input_evaluation_action = _descriptors.Single["AbstractAction"](
        _descriptors.Association((NS, "AbstractAction"), "inputEvaluationAction")
    )


class ValuePin(InputPin, abstract=True):
    value = _descriptors.Single["modellingcore.ValueSpecification"](
        _descriptors.Containment("value", (ns.MODELLINGCORE, "ValueSpecification"))
    )


class OutputPin(Pin, abstract=True):
    pass
