# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
"""Objects and relations for information capture and data modelling."""

from __future__ import annotations

import enum
import typing as t

import capellambse.model as m
from capellambse.model import _descriptors, _obj, _pods

from .. import behavior, capellacore, modellingcore
from .. import namespaces as ns

NS = ns.INFORMATION
NS_DV = ns.INFORMATION_DATAVALUE
NS_DT = ns.INFORMATION_DATATYPE
NS_COMM = ns.INFORMATION_COMMUNICATION


@m.stringy_enum
@enum.unique
class AggregationKind(enum.Enum):
    """Defines the specific kind of a relationship, as per UML definitions."""

    UNSET = "UNSET"
    """Used when value is not defined by the user."""
    ASSOCIATION = "ASSOCIATION"
    """A semantic relationship between typed instances.

    It has at least two ends represented by properties, each of which is
    connected to the type of the end. More than one end of the
    association may have the same type.

    Indicates that the property has no aggregation.
    """
    AGGREGATION = "AGGREGATION"
    """A semantic relationship between a part and a whole.

    The part has a lifecycle of its own, and is potentially shared among
    several aggregators.
    """
    COMPOSITION = "COMPOSITION"
    """A semantic relationship between whole and its parts.

    The parts lifecycles are tied to that of the whole, and they are not
    shared with any other aggregator.
    """


@m.stringy_enum
@enum.unique
class CollectionKind(enum.Enum):
    """Defines the specific kind of a Collection structure."""

    ARRAY = "ARRAY"
    """The collection is to be considered an array of elements."""
    SEQUENCE = "SEQUENCE"
    """The collection is to be considered as a sequence (list) of elements."""


@m.stringy_enum
@enum.unique
class ElementKind(enum.Enum):
    """The visibility options for features of a class."""

    TYPE = "TYPE"
    """The ExchangeItemElement is a type for its ExchangeItem."""
    MEMBER = "MEMBER"
    """The ExchangeItemElement is a member for its ExchangeItem."""


@m.stringy_enum
@enum.unique
class ExchangeMechanism(enum.Enum):
    """Enumeration of the different exchange mechanisms."""

    UNSET = "UNSET"
    """The exchange mechanism is not defined."""
    FLOW = "FLOW"
    """Continuous supply of data."""
    OPERATION = "OPERATION"
    """Sporadic supply of data with returned data."""
    EVENT = "EVENT"
    """Asynchronous information that is taken into account rapidly."""
    SHARED_DATA = "SHARED_DATA"


@m.stringy_enum
@enum.unique
class ParameterDirection(enum.Enum):
    """The direction in which data is passed along through a parameter."""

    IN = "IN"
    """The parameter represents an input of the operation it is used in."""
    OUT = "OUT"
    """The parameter represents an output of the operation it is used in."""
    INOUT = "INOUT"
    """The parameter represents both an input and output of the operation."""
    RETURN = "RETURN"
    """The parameter represents the return value of the operation."""
    EXCEPTION = "EXCEPTION"
    """The parameter is like an exception."""
    UNSET = "UNSET"
    """The CommunicationLink protocol is not yet set."""


@m.stringy_enum
@enum.unique
class PassingMode(enum.Enum):
    """The data passing mechanism for parameters of an operation."""

    UNSET = "UNSET"
    """The data passing mechanism is not precised."""
    BY_REF = "BY_REF"
    """The data is being passed by reference to the operation."""
    BY_VALUE = "BY_VALUE"
    """The data is being passed by value to the operation."""


@m.stringy_enum
@enum.unique
class SynchronismKind(enum.Enum):
    """The synchronicity of an operation invocation."""

    UNSET = "UNSET"
    SYNCHRONOUS = "SYNCHRONOUS"
    ASYNCHRONOUS = "ASYNCHRONOUS"


@m.stringy_enum
@enum.unique
class UnionKind(enum.Enum):
    UNION = "UNION"
    VARIANT = "VARIANT"


class MultiplicityElement(capellacore.CapellaElement, abstract=True):
    is_ordered = _pods.BoolPOD("ordered")
    """Indicates if this element is ordered."""
    is_unique = _pods.BoolPOD("unique")
    """Indicates if this element is unique."""
    is_min_inclusive = _pods.BoolPOD("minInclusive")
    is_max_inclusive = _pods.BoolPOD("maxInclusive")
    default_value = _descriptors.Single["datavalue.DataValue"](
        _descriptors.Containment("ownedDefaultValue", (NS_DV, "DataValue"))
    )
    min_value = _descriptors.Single["datavalue.DataValue"](
        _descriptors.Containment("ownedMinValue", (NS_DV, "DataValue"))
    )
    max_value = _descriptors.Single["datavalue.DataValue"](
        _descriptors.Containment("ownedMaxValue", (NS_DV, "DataValue"))
    )
    null_value = _descriptors.Single["datavalue.DataValue"](
        _descriptors.Containment("ownedNullValue", (NS_DV, "DataValue"))
    )
    min_card = _descriptors.Single["datavalue.NumericValue"](
        _descriptors.Containment("ownedMinCard", (NS_DV, "NumericValue"))
    )
    min_length = _descriptors.Single["datavalue.NumericValue"](
        _descriptors.Containment("ownedMinLength", (NS_DV, "NumericValue"))
    )
    max_card = _descriptors.Single["datavalue.NumericValue"](
        _descriptors.Containment("ownedMaxCard", (NS_DV, "NumericValue"))
    )
    max_length = _descriptors.Single["datavalue.NumericValue"](
        _descriptors.Containment("ownedMaxLength", (NS_DV, "NumericValue"))
    )


class Property(
    capellacore.Feature,
    capellacore.TypedElement,
    MultiplicityElement,
    modellingcore.FinalizableElement,
):
    """A Property of a Class."""

    _xmltag = "ownedFeatures"

    aggregation_kind = _pods.EnumPOD("aggregationKind", AggregationKind)
    is_derived = _pods.BoolPOD("isDerived")
    """Indicates if property is abstract."""
    is_read_only = _pods.BoolPOD("isReadOnly")
    """Indicates if property is read-only."""
    is_part_of_key = _pods.BoolPOD("isPartOfKey")
    """Indicates if property is part of key."""
    association = _descriptors.Single["Association"](
        _descriptors.Backref((NS, "Association"), "roles")
    )

    if not t.TYPE_CHECKING:
        kind = _descriptors.DeprecatedAccessor("aggregation_kind")


class AbstractInstance(Property, abstract=True):
    pass


class AssociationPkg(capellacore.Structure, abstract=True):
    visibility = _pods.EnumPOD("visibility", capellacore.VisibilityKind)
    associations = _descriptors.Containment["Association"](
        "ownedAssociations", (NS, "Association")
    )


class Association(capellacore.NamedRelationship):
    _xmltag = "ownedAssociations"

    members = _descriptors.Containment["Property"]("ownedMembers", (NS, "Property"))
    navigable_members = _descriptors.Association["Property"](
        (NS, "Property"), "navigableMembers"
    )

    @property
    def roles(self) -> _obj.ElementList[Property]:
        assert isinstance(self.members, _obj.ElementList)
        assert isinstance(self.navigable_members, _obj.ElementList)
        roles = [i._element for i in self.members + self.navigable_members]
        return _obj.ElementList(self._model, roles, Property)


class Class(capellacore.GeneralClass):
    _xmltag = "ownedClasses"

    is_primitive = _pods.BoolPOD("isPrimitive")
    """Indicates if class is primitive."""
    key_parts = _descriptors.Association["KeyPart"]((NS, "KeyPart"), "keyParts")
    state_machines = _descriptors.Containment["capellacommon.StateMachine"](
        "ownedStateMachines", (ns.CAPELLACOMMON, "StateMachine")
    )
    data_values = _descriptors.Containment["datavalue.DataValue"](
        "ownedDataValues", (NS_DV, "DataValue")
    )
    information_realizations = _descriptors.Containment["InformationRealization"](
        "ownedInformationRealizations", (NS, "InformationRealization")
    )
    realized_classes = _descriptors.Allocation["Class"](
        "ownedInformationRealizations",
        (NS, "InformationRealization"),
        (NS, "Class"),
        attr="targetElement",
        backattr="sourceElement",
    )
    realized_by = _descriptors.Backref["Class"]((NS, "Class"), "realized_classes")

    owned_properties = _descriptors.Filter["Property"]("owned_features", (NS, "Property"))

    @property
    def properties(self) -> _obj.ElementList[Property]:
        """Return all owned and inherited properties."""
        return (
            self.owned_properties + self.super.properties
            if self.super is not None
            else self.owned_properties
        )

    if not t.TYPE_CHECKING:
        realizations = _descriptors.DeprecatedAccessor("information_realizations")


from . import datavalue as datavalue


class Collection(
    capellacore.Classifier,
    MultiplicityElement,
    datavalue.DataValueContainer,
    modellingcore.FinalizableElement,
):
    """A Collection."""

    _xmltag = "ownedCollections"

    is_primitive = _pods.BoolPOD("isPrimitive")
    visibility = _pods.EnumPOD("visibility", capellacore.VisibilityKind)
    kind = _pods.EnumPOD("kind", CollectionKind)
    aggregation_kind = _pods.EnumPOD("aggregationKind", AggregationKind)
    type = _descriptors.Association["capellacore.Type"]((ns.CAPELLACORE, "Type"), "type")
    index = _descriptors.Association["datatype.DataType"]((NS_DT, "DataType"), "index")


class AbstractCollectionValue(datavalue.DataValue, abstract=True):
    pass


class CollectionValue(AbstractCollectionValue):
    elements = _descriptors.Containment["datavalue.DataValue"](
        "ownedElements", (NS_DV, "DataValue")
    )
    default_element = _descriptors.Containment["datavalue.DataValue"](
        "ownedDefaultElement", (NS_DV, "DataValue")
    )


class CollectionValueReference(AbstractCollectionValue):
    value = _descriptors.Association["AbstractCollectionValue"](
        (NS, "AbstractCollectionValue"), "referencedValue"
    )
    property = _descriptors.Association["Property"](
        (NS, "Property"), "referencedProperty"
    )


from . import communication as communication


class DataPkg(
    capellacore.AbstractDependenciesPkg,
    capellacore.AbstractExchangeItemPkg,
    AssociationPkg,
    datavalue.DataValueContainer,
    communication.MessageReferencePkg,
):
    """A data package that can hold classes."""

    _xmltag = "ownedDataPkgs"

    packages = _descriptors.Containment["DataPkg"]("ownedDataPkgs", (NS, "DataPkg"))
    classes = _descriptors.Containment["Class"]("ownedClasses", (NS, "Class"))
    unions = _descriptors.Filter["Union"]("classes", (NS, "Union"))
    key_parts = _descriptors.Containment["KeyPart"]("ownedKeyParts", (NS, "KeyPart"))
    collections = _descriptors.Containment["Collection"](
        "ownedCollections", (NS, "Collection")
    )
    units = _descriptors.Containment["Unit"]("ownedUnits", (NS, "Unit"))
    data_types = _descriptors.Containment["datatype.DataType"](
        "ownedDataTypes", (NS_DT, "DataType")
    )
    enumerations = _descriptors.Filter["datatype.Enumeration"](
        "data_types", (NS_DT, "Enumeration")
    )
    signals = _descriptors.Containment["communication.Signal"](
        "ownedSignals", (NS_COMM, "Signal")
    )
    messages = _descriptors.Containment["communication.Message"](
        "ownedMessages", (NS_COMM, "Message")
    )
    exceptions = _descriptors.Containment["communication.Exception"](
        "ownedExceptions", (NS_COMM, "Exception")
    )
    state_events = _descriptors.Containment["capellacommon.StateEvent"](
        "ownedStateEvents", (ns.CAPELLACOMMON, "StateEvent")
    )

    if not t.TYPE_CHECKING:
        datatypes = _descriptors.DeprecatedAccessor("data_types")
        owned_associations = _descriptors.DeprecatedAccessor("associations")


class DomainElement(Class):
    pass


class KeyPart(capellacore.Relationship):
    property = _descriptors.Single["Property"](
        _descriptors.Association((NS, "Property"), "property")
    )


class AbstractEventOperation(capellacore.NamedElement, abstract=True):
    pass


class Operation(
    capellacore.Feature,
    behavior.AbstractEvent,
    AbstractEventOperation,
    abstract=True,
):
    parameters = _descriptors.Containment["Parameter"](
        "ownedParameters", (NS, "Parameter")
    )
    operation_allocations = _descriptors.Containment["OperationAllocation"](
        "ownedOperationAllocation", (NS, "OperationAllocation")
    )
    allocated_operations = _descriptors.Allocation["Operation"](
        "ownedOperationAllocation",
        (NS, "OperationAllocation"),
        (NS, "Operation"),
        attr="targetElement",
        backattr="sourceElement",
    )
    allocating_operations = _descriptors.Backref["Operation"](
        (NS, "Operation"), "allocated_operations"
    )
    exchange_item_realizations = _descriptors.Containment["ExchangeItemRealization"](
        "ownedExchangeItemRealizations", (NS, "ExchangeItemRealization")
    )
    realized_exchange_items = _descriptors.Allocation["ExchangeItem"](
        "ownedExchangeItemRealizations",
        (NS, "ExchangeItemRealization"),
        (NS, "ExchangeItem"),
        attr="targetElement",
        backattr="sourceElement",
    )


class OperationAllocation(capellacore.Allocation):
    pass


class Parameter(
    capellacore.TypedElement,
    MultiplicityElement,
    modellingcore.AbstractParameter,
):
    direction = _pods.EnumPOD("direction", ParameterDirection)
    passing_mode = _pods.EnumPOD("passingMode", PassingMode)


class Service(Operation):
    synchronism_kind = _pods.EnumPOD("synchronismKind", SynchronismKind)
    thrown_exceptions = _descriptors.Association["communication.Exception"](
        (NS_COMM, "Exception"), "thrownExceptions"
    )
    message_references = _descriptors.Association["communication.MessageReference"](
        (NS_COMM, "MessageReference"), "messageReferences"
    )


class Union(Class):
    """A Union."""

    _xmltag = "ownedClasses"

    kind = _pods.EnumPOD("kind", UnionKind)
    discriminant = _descriptors.Association["UnionProperty"](
        (NS, "UnionProperty"), "discriminant"
    )
    default_property = _descriptors.Association["UnionProperty"](
        (NS, "UnionProperty"), "defaultProperty"
    )


class UnionProperty(Property):
    qualifier = _descriptors.Association["datavalue.DataValue"](
        (NS_DV, "DataValue"), "qualifier"
    )


class Unit(capellacore.NamedElement):
    _xmltag = "ownedUnits"


class Port(capellacore.NamedElement, abstract=True):
    protocols = _descriptors.Containment["capellacommon.StateMachine"](
        "ownedProtocols", (ns.CAPELLACOMMON, "StateMachine")
    )
    provided_interfaces = _descriptors.Association["cs.Interface"](
        (ns.CS, "Interface"), "providedInterfaces"
    )
    required_interfaces = _descriptors.Association["cs.Interface"](
        (ns.CS, "Interface"), "requiredInterfaces"
    )
    port_realizations = _descriptors.Containment["PortRealization"](
        "ownedPortRealizations", (NS, "PortRealization")
    )
    realized_ports = _descriptors.Allocation["Port"](
        "ownedPortRealizations",
        (NS, "PortRealization"),
        (NS, "Port"),
        attr="targetElement",
        backattr="sourceElement",
    )
    port_allocations = _descriptors.Containment["PortAllocation"](
        "ownedPortAllocations", (NS, "PortAllocation")
    )
    allocated_ports = _descriptors.Allocation["Port"](
        "ownedPortRealizations",
        (NS, "PortRealization"),
        (NS, "Port"),
        attr="targetElement",
        backattr="sourceElement",
    )

    if not t.TYPE_CHECKING:
        state_machines = _descriptors.DeprecatedAccessor("protocols")


class PortRealization(capellacore.Allocation):
    pass


class PortAllocation(capellacore.Allocation):
    _xmltag = "ownedPortAllocations"


class ExchangeItem(
    modellingcore.AbstractExchangeItem,
    behavior.AbstractEvent,
    behavior.AbstractSignal,
    modellingcore.FinalizableElement,
    capellacore.GeneralizableElement,
):
    _xmltag = "ownedExchangeItems"

    exchange_mechanism = _pods.EnumPOD("exchangeMechanism", ExchangeMechanism)
    elements = _descriptors.Containment["ExchangeItemElement"](
        "ownedElements", (NS, "ExchangeItemElement")
    )
    information_realizations = _descriptors.Containment["InformationRealization"](
        "ownedInformationRealizations", (NS, "InformationRealization")
    )
    instances = _descriptors.Containment["ExchangeItemInstance"](
        "ownedExchangeItemInstances", (NS, "ExchangeItemInstance")
    )

    @property
    def exchanges(
        self,
    ) -> _obj.ElementList[fa.ComponentExchange | fa.FunctionalExchange]:
        """Exchanges using this ExchangeItem."""
        CX = (ns.FA, "ComponentExchange")
        FX = (ns.FA, "FunctionalExchange")
        cxs = self._model.search(CX).by_convoyed_informations(self)
        fxs = self._model.search(FX).by_exchanged_items(self)
        return cxs + fxs

    if not t.TYPE_CHECKING:
        type = _descriptors.DeprecatedAccessor("exchange_mechanism")


class ExchangeItemElement(
    MultiplicityElement, capellacore.TypedElement, capellacore.NamedElement
):
    _xmltag = "ownedElements"

    kind = _pods.EnumPOD("kind", ElementKind)
    direction = _pods.EnumPOD("direction", ParameterDirection)
    is_composite = _pods.BoolPOD("composite")
    referenced_properties = _descriptors.Association["Property"](
        (NS, "Property"), "referencedProperties"
    )

    if not t.TYPE_CHECKING:
        abstract_type = _descriptors.DeprecatedAccessor("type")
        owner = _descriptors.DeprecatedAccessor("parent")


class ExchangeItemInstance(AbstractInstance):
    pass


class InformationRealization(capellacore.Allocation):
    _xmltag = "ownedInformationRealizations"


class ExchangeItemRealization(capellacore.Allocation):
    pass


from .. import capellacommon, cs, fa  # noqa: F401
from . import datatype as datatype
