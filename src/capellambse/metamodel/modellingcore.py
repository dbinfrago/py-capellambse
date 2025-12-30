# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import enum

import capellambse.model as m
from capellambse.model import _descriptors, _pods
from capellambse.model._obj import ModelElement as ModelElement

from . import namespaces as ns

NS = ns.MODELLINGCORE


@m.stringy_enum
@enum.unique
class ParameterEffectKind(enum.Enum):
    """A behavior's effect on values passed in or out of its parameters."""

    READ = "read"
    """The parameter value is only being read upon behavior execution."""
    UPDATE = "update"
    """The parameter value is being updated upon behavior execution."""
    CREATE = "create"
    """The parameter value is being created upon behavior execution."""
    DELETE = "delete"
    """The parameter value is being deleted upon behavior execution."""


@m.stringy_enum
@enum.unique
class RateKind(enum.Enum):
    """The possible caracterizations for the rate of a streaming parameter."""

    UNSPECIFIED = "Unspecified"
    """The rate kind is not specified."""
    CONTINUOUS = "Continuous"
    """The rate characterizes a continuous flow."""
    DISCRETE = "Discrete"
    """The rate characterizes a discrete flow."""


ModelElement.extensions = _descriptors.Containment["ModelElement"](
    "ownedExtensions", (NS, "ModelElement")
)
ModelElement.constraints = _descriptors.Containment(
    "ownedConstraints", (ns.CAPELLACORE, "Constraint")
)
ModelElement.migrated_elements = _descriptors.Containment["ModelElement"](
    "ownedMigratedElements", (NS, "ModelElement")
)


class AbstractRelationship(ModelElement, abstract=True):
    realized_flow = _descriptors.Association["AbstractInformationFlow"](
        (NS, "AbstractInformationFlow"), "realizedFlow"
    )


class AbstractNamedElement(ModelElement, abstract=True):
    """An element that may have a name.

    The name is used for identification of the named element within the
    namespace in which it is defined. A named element also has a
    qualified name that allows it to be unambiguously identified within
    a hierarchy of nested namespaces.
    """

    name = _pods.StringPOD("name")


class InformationsExchanger(ModelElement, abstract=True):
    """An element that may exchange information with other elements."""


class TraceableElement(ModelElement, abstract=True):
    """An element that may be traced to other elements."""


class FinalizableElement(ModelElement, abstract=True):
    is_final = _pods.BoolPOD("final")


class PublishableElement(ModelElement, abstract=True):
    is_visible_in_doc = _pods.BoolPOD("visibleInDoc")
    is_visible_in_lm = _pods.BoolPOD("visibleInLM")


class AbstractType(AbstractNamedElement, abstract=True):
    """Base abstract class supporting the definition of data types."""


class AbstractTypedElement(AbstractNamedElement, abstract=True):
    """A (named) model element to which a specific type is associated."""

    type: _descriptors.Single[AbstractType] = _descriptors.Single["AbstractType"](
        _descriptors.Association((NS, "AbstractType"), "abstractType")
    )


class AbstractTrace(TraceableElement, abstract=True):
    target = _descriptors.Single["TraceableElement"](
        _descriptors.Association((NS, "TraceableElement"), "targetElement")
    )
    source = _descriptors.Single["TraceableElement"](
        _descriptors.Association((NS, "TraceableElement"), "sourceElement")
    )


class AbstractConstraint(ModelElement, abstract=True):
    """A constraint that applies to a given set of model elements."""

    constrained_elements = _descriptors.Association["ModelElement"](
        (NS, "ModelElement"), "constrainedElements", legacy_by_type=True
    )
    specification = _descriptors.Single["ValueSpecification"](
        _descriptors.Containment("ownedSpecification", (NS, "ValueSpecification"))
    )
    """A condition that must evaluate to true to satisfy the constraint."""


class ValueSpecification(AbstractTypedElement, abstract=True):
    """The specification of a set of instances.

    The set includes both objects and data values, and may be empty.
    """


class AbstractParameter(AbstractTypedElement, abstract=True):
    """Specification of an argument to a behavioral feature.

    Parameters are used to pass information into or out of an invocation
    of a behavioral feature.
    """

    is_exception = _pods.BoolPOD("isException")
    is_stream = _pods.BoolPOD("isStream")
    is_optional = _pods.BoolPOD("isOptional")
    kind_of_rate = _pods.EnumPOD("kindOfRate", RateKind)
    effect = _pods.EnumPOD("effect", ParameterEffectKind)
    rate = _descriptors.Single["ValueSpecification"](
        _descriptors.Containment("rate", (NS, "ValueSpecification"))
    )
    probability = _descriptors.Single["ValueSpecification"](
        _descriptors.Containment("probability", (NS, "ValueSpecification"))
    )
    parameter_set = _descriptors.Single["AbstractParameterSet"](
        _descriptors.Association((NS, "AbstractParameterSet"), "parameterSet")
    )


class AbstractParameterSet(AbstractNamedElement, abstract=True):
    """An alternative set of inputs or outputs that a behavior may use."""

    conditions = _descriptors.Containment["AbstractConstraint"](
        "ownedConditions", (NS, "AbstractConstraint")
    )
    probability = _descriptors.Single["ValueSpecification"](
        _descriptors.Containment("probability", (NS, "ValueSpecification"))
    )
    parameters = _descriptors.Single["AbstractParameter"](
        _descriptors.Association((NS, "AbstractParameter"), "parameters")
    )


class AbstractInformationFlow(
    AbstractNamedElement, AbstractRelationship, abstract=True
):
    realizations = _descriptors.Association["AbstractRelationship"](
        (NS, "AbstractRelationship"), "realizations"
    )
    convoyed_informations = _descriptors.Association["AbstractExchangeItem"](
        (NS, "AbstractExchangeItem"), "convoyedInformations"
    )
    source = _descriptors.Single["InformationsExchanger"](
        _descriptors.Association((NS, "InformationsExchanger"), "source")
    )
    target = _descriptors.Single["InformationsExchanger"](
        _descriptors.Association((NS, "InformationsExchanger"), "target")
    )


class AbstractExchangeItem(AbstractType, abstract=True):
    """Set of exchanged element exchanged between ports."""


class IState(AbstractNamedElement, abstract=True):
    """A vertex is an abstraction of a node in a state machine graph.

    In general, it can be the source or destination of any number of
    transitions.
    """

    referenced_states = _descriptors.Association["IState"](
        (NS, "IState"), "referencedStates"
    )
    exploited_states = _descriptors.Association["IState"](
        (NS, "IState"), "exploitedStates"
    )
