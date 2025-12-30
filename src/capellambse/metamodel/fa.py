# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import enum
import sys
import typing as t
import warnings

import capellambse.model as m
from capellambse.model import _descriptors, _obj, _pods

from . import activity, behavior, capellacore, information, modellingcore
from . import namespaces as ns

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

NS = ns.FA


# TODO Remove _AbstractExchange when removing deprecated features
class _AbstractExchange(_obj.ModelElement):
    if not t.TYPE_CHECKING:

        @property
        def source(self) -> _obj.ModelElement:
            raise TypeError(
                "AbstractExchange is deprecated and will be removed soon,"
                " use the concrete FunctionalExchange or ComponentExchange"
                " class or another common superclass instead"
            )

        @property
        def target(self) -> _obj.ModelElement:
            raise TypeError(
                "AbstractExchange is deprecated and will be removed soon,"
                " use the concrete FunctionalExchange or ComponentExchange"
                " class or another common superclass instead"
            )


@m.stringy_enum
@enum.unique
class ComponentExchangeKind(enum.Enum):
    """The kind of a ComponentExchange."""

    UNSET = "UNSET"
    """Communication kind is not set."""
    DELEGATION = "DELEGATION"
    """Indicates that the connector is a delegation connector."""
    ASSEMBLY = "ASSEMBLY"
    """Indicates that the connector is an assembly connector."""
    FLOW = "FLOW"
    """Describes a flow communication."""


@m.stringy_enum
@enum.unique
class ComponentPortKind(enum.Enum):
    STANDARD = "STANDARD"
    """Describes a standard port.

    A port is an interaction point between a Block or sub-Block and its
    environment that supports Exchanges with other ports.
    """
    FLOW = "FLOW"
    """Describes a flow port.

    A flow port is an interaction point through which input and/or
    output of items such as data, material, or energy may flow.
    """


@m.stringy_enum
@enum.unique
class ControlNodeKind(enum.Enum):
    OR = "OR"
    AND = "AND"
    ITERATE = "ITERATE"


@m.stringy_enum
@enum.unique
class FunctionKind(enum.Enum):
    """The kind of a Function."""

    FUNCTION = "FUNCTION"
    DUPLICATE = "DUPLICATE"
    GATHER = "GATHER"
    SELECT = "SELECT"
    SPLIT = "SPLIT"
    ROUTE = "ROUTE"


@m.stringy_enum
@enum.unique
class FunctionalChainKind(enum.Enum):
    """The kind of a Functional Chain."""

    SIMPLE = "SIMPLE"
    COMPOSITE = "COMPOSITE"
    FRAGMENT = "FRAGMENT"


@m.stringy_enum
@enum.unique
class OrientationPortKind(enum.Enum):
    """Direction of component ports."""

    UNSET = "UNSET"
    """The port orientation is undefined."""
    IN = "IN"
    """The port represents an input of the component it is used in."""
    OUT = "OUT"
    """The port represents an output of the component it is used in."""
    INOUT = "INOUT"
    """The port represents both an input and on output of the component."""


class AbstractFunctionalArchitecture(
    capellacore.ModellingArchitecture, abstract=True
):
    function_pkg = _descriptors.Single["FunctionPkg"](
        _descriptors.Containment("ownedFunctionPkg", (NS, "FunctionPkg"))
    )
    component_exchanges = _descriptors.Containment["ComponentExchange"](
        "ownedComponentExchanges", (NS, "ComponentExchange")
    )
    component_exchange_categories = _descriptors.Containment["ComponentExchangeCategory"](
        "ownedComponentExchangeCategories", (NS, "ComponentExchangeCategory")
    )
    functional_links = _descriptors.Containment["ExchangeLink"](
        "ownedFunctionalLinks", (NS, "ExchangeLink")
    )
    functional_allocations = _descriptors.Containment["ComponentFunctionalAllocation"](
        "ownedFunctionalAllocations", (NS, "ComponentFunctionalAllocation")
    )
    component_exchange_realizations = _descriptors.Containment[
        "ComponentExchangeRealization"
    ](
        "ownedComponentExchangeRealizations",
        (NS, "ComponentExchangeRealization"),
    )

    @property
    def all_functions(self) -> _obj.ElementList[AbstractFunction]:
        return self._model.search((NS, "AbstractFunction"), below=self)

    @property
    def all_functional_chains(self) -> _obj.ElementList[FunctionalChain]:
        return self._model.search((NS, "FunctionalChain"), below=self)

    @property
    def all_function_exchanges(self) -> _obj.ElementList[FunctionalExchange]:
        return self._model.search((NS, "FunctionalExchange"), below=self)

    if not t.TYPE_CHECKING:
        function_package = _descriptors.DeprecatedAccessor("function_pkg")


class AbstractFunctionalBlock(capellacore.ModellingBlock, abstract=True):
    functional_allocations = _descriptors.Containment["ComponentFunctionalAllocation"](
        "ownedFunctionalAllocation", (NS, "ComponentFunctionalAllocation")
    )
    allocated_functions = _descriptors.Allocation["AbstractFunction"](
        "ownedFunctionalAllocation",
        (NS, "ComponentFunctionalAllocation"),
        (NS, "AbstractFunction"),
        attr="targetElement",
        backattr="sourceElement",
    )
    component_exchanges = _descriptors.Containment["ComponentExchange"](
        "ownedComponentExchanges", (NS, "ComponentExchange")
    )
    component_exchange_categories = _descriptors.Containment["ComponentExchangeCategory"](
        "ownedComponentExchangeCategories", (NS, "ComponentExchangeCategory")
    )
    in_exchange_links = _descriptors.Association["ExchangeLink"](
        (NS, "ExchangeLink"), "inExchangeLinks"
    )
    out_exchange_links = _descriptors.Association["ExchangeLink"](
        (NS, "ExchangeLink"), "outExchangeLinks"
    )


class FunctionPkg(capellacore.Structure, abstract=True):
    functional_links = _descriptors.Containment["ExchangeLink"](
        "ownedFunctionalLinks", (NS, "ExchangeLink")
    )
    exchanges = _descriptors.Containment["FunctionalExchangeSpecification"](
        "ownedExchanges", (NS, "FunctionalExchangeSpecification")
    )
    exchange_specification_realizations = _descriptors.Containment[
        "ExchangeSpecificationRealization"
    ](
        "ownedExchangeSpecificationRealizations",
        (NS, "ExchangeSpecificationRealization"),
    )
    realized_exchange_specifications = _descriptors.Allocation["ExchangeSpecification"](
        "ownedExchangeSpecificationRealizations",
        (NS, "ExchangeSpecificationRealization"),
        (NS, "ExchangeSpecification"),
        attr="targetElement",
        backattr="sourceElement",
    )
    categories = _descriptors.Containment["ExchangeCategory"](
        "ownedCategories", (NS, "ExchangeCategory")
    )
    function_specifications = _descriptors.Containment["FunctionSpecification"](
        "ownedFunctionSpecifications", (NS, "FunctionSpecification")
    )


class FunctionSpecification(capellacore.Namespace, activity.AbstractActivity):
    in_exchange_links = _descriptors.Association["ExchangeLink"](
        (NS, "ExchangeLink"), "inExchangeLinks"
    )
    out_exchange_links = _descriptors.Association["ExchangeLink"](
        (NS, "ExchangeLink"), "outExchangeLinks"
    )
    ports = _descriptors.Containment["FunctionPort"](
        "ownedFunctionPorts", (NS, "FunctionPort")
    )


class ExchangeCategory(capellacore.NamedElement):
    _xmltag = "ownedCategories"

    exchanges = _descriptors.Association["FunctionalExchange"](
        (NS, "FunctionalExchange"), "exchanges"
    )


class ExchangeLink(capellacore.NamedRelationship):
    exchange_containment_links = _descriptors.Association["ExchangeContainment"](
        (NS, "ExchangeContainment"), "exchangeContainmentLinks"
    )
    exchange_containments = _descriptors.Containment["ExchangeContainment"](
        "ownedExchangeContainments", (NS, "ExchangeContainment")
    )
    sources = _descriptors.Association["FunctionSpecification"](
        (NS, "FunctionSpecification"), "sources"
    )
    destinations = _descriptors.Association["FunctionSpecification"](
        (NS, "FunctionSpecification"), "destinations"
    )


class ExchangeContainment(capellacore.Relationship):
    exchange = _descriptors.Single["ExchangeSpecification"](
        _descriptors.Association((NS, "ExchangeSpecification"), "exchange")
    )
    link = _descriptors.Single["ExchangeLink"](
        _descriptors.Association((NS, "ExchangeLink"), "link")
    )


class ExchangeSpecification(
    capellacore.NamedElement, activity.ActivityExchange, abstract=True
):
    link = _descriptors.Association["ExchangeContainment"](
        (NS, "ExchangeContainment"), "link"
    )


class FunctionalExchangeSpecification(ExchangeSpecification):
    pass


class FunctionalChain(
    capellacore.NamedElement,
    capellacore.InvolverElement,
    capellacore.InvolvedElement,
):
    _xmltag = "ownedFunctionalChains"

    kind = _pods.EnumPOD("kind", FunctionalChainKind)
    involvements = _descriptors.Containment["FunctionalChainInvolvement"](
        "ownedFunctionalChainInvolvements", (NS, "FunctionalChainInvolvement")
    )

    @property
    def involved_functions(self) -> _obj.ElementList[AbstractFunction]:
        objs = self.involvements.map("involved").by_class(AbstractFunction)
        return _obj.ElementList(self._model, objs._elements, legacy_by_type=True)

    @property
    def involved_links(self) -> _obj.ElementList[FunctionalExchange]:
        objs = self.involvements.map("involved").by_class(FunctionalExchange)
        return _obj.ElementList(self._model, objs._elements, legacy_by_type=True)

    @property
    def involved_chains(self) -> _obj.ElementList[FunctionalChain]:
        return self.involvements.map("involved").by_class(FunctionalChain)

    @property
    def involved(self) -> _obj.ElementList[AbstractFunction | FunctionalExchange]:
        objs = self.involvements.map("involved").by_class(
            AbstractFunction, FunctionalExchange
        )
        return _obj.ElementList(self._model, objs._elements, legacy_by_type=True)

    involving_chains = _descriptors.Backref["FunctionalChain"](
        (NS, "FunctionalChain"), "involved_chains"
    )

    functional_chain_realizations = _descriptors.Containment[
        "FunctionalChainRealization"
    ]("ownedFunctionalChainRealizations", (NS, "FunctionalChainRealization"))
    realized_chains = _descriptors.Allocation["FunctionalChain"](
        "ownedFunctionalChainRealizations",
        (NS, "FunctionalChainRealization"),
        (NS, "FunctionalChain"),
        attr="targetElement",
        backattr="sourceElement",
    )
    realizing_chains = _descriptors.Backref["FunctionalChain"](
        (NS, "FunctionalChain"), "realized_chains"
    )
    available_in_states = _descriptors.Association["capellacommon.State"](
        (ns.CAPELLACOMMON, "State"), "availableInStates"
    )
    precondition = _descriptors.Single["capellacore.Constraint"](
        _descriptors.Association((ns.CAPELLACORE, "Constraint"), "preCondition")
    )
    postcondition = _descriptors.Single["capellacore.Constraint"](
        _descriptors.Association((ns.CAPELLACORE, "Constraint"), "postCondition")
    )
    sequence_nodes = _descriptors.Containment["ControlNode"](
        "ownedSequenceNodes", (NS, "ControlNode")
    )
    sequence_links = _descriptors.Containment["SequenceLink"](
        "ownedSequenceLinks", (NS, "SequenceLink")
    )

    if not t.TYPE_CHECKING:
        control_nodes = _descriptors.DeprecatedAccessor("sequence_nodes")


class AbstractFunctionalChainContainer(
    capellacore.CapellaElement, abstract=True
):
    functional_chains = _descriptors.Containment["FunctionalChain"](
        "ownedFunctionalChains", (NS, "FunctionalChain")
    )


class FunctionalChainInvolvement(capellacore.Involvement, abstract=True):
    _xmltag = "ownedFunctionalChainInvolvements"


class FunctionalChainReference(FunctionalChainInvolvement):
    involved = _descriptors.Single["FunctionalChain"](
        _descriptors.Association((NS, "FunctionalChain"), None)
    )


class FunctionPort(
    information.Port,
    capellacore.TypedElement,
    behavior.AbstractEvent,
    abstract=True,
):
    represented_component_port = _descriptors.Single["ComponentPort"](
        _descriptors.Association((NS, "ComponentPort"), "representedComponentPort")
    )
    realized_ports = _descriptors.Allocation["FunctionPort"](
        None, None, (NS, "FunctionPort")
    )
    allocated_ports = _descriptors.Allocation["FunctionPort"](
        None, None, (NS, "FunctionPort")
    )
    exchanges = _descriptors.Backref["FunctionalExchange"](
        (NS, "FunctionalExchange"), "source", "target"
    )

    if not t.TYPE_CHECKING:
        owner = _descriptors.DeprecatedAccessor("parent")


class FunctionInputPort(FunctionPort, activity.InputPin):
    """A function input port."""

    _xmltag = "inputs"

    exchange_items = _descriptors.Association["information.ExchangeItem"](
        (ns.INFORMATION, "ExchangeItem"), "incomingExchangeItems"
    )


class FunctionOutputPort(FunctionPort, activity.OutputPin):
    """A function output port."""

    _xmltag = "outputs"

    exchange_items = _descriptors.Association["information.ExchangeItem"](
        (ns.INFORMATION, "ExchangeItem"), "outgoingExchangeItems"
    )


class AbstractFunctionAllocation(capellacore.Allocation, abstract=True):
    pass


class ComponentFunctionalAllocation(AbstractFunctionAllocation):
    pass


class FunctionalChainRealization(capellacore.Allocation):
    pass


class ExchangeSpecificationRealization(capellacore.Allocation, abstract=True):
    pass


class FunctionalExchangeRealization(capellacore.Allocation):
    pass


class FunctionRealization(AbstractFunctionAllocation):
    """A realization that links to a function."""

    _xmltag = "ownedFunctionRealizations"


class FunctionalExchange(
    capellacore.Relationship,
    capellacore.InvolvedElement,
    activity.ObjectFlow,
    behavior.AbstractEvent,
    information.AbstractEventOperation,
    # NOTE: NamedElement is first in the upstream metamodel,
    # but that would result in an MRO conflict with AbstractEventOperation,
    # which inherits from NamedElement.
    capellacore.NamedElement,
    _AbstractExchange,
):
    _xmltag = "ownedFunctionalExchanges"

    exchange_specifications = _descriptors.Association["FunctionalExchangeSpecification"](
        (NS, "FunctionalExchangeSpecification"), "exchangeSpecifications"
    )
    exchanged_items = _descriptors.Association["information.ExchangeItem"](
        (ns.INFORMATION, "ExchangeItem"), "exchangedItems"
    )
    functional_exchange_realizations = _descriptors.Containment[
        "FunctionalExchangeRealization"
    ](
        "ownedFunctionalExchangeRealizations",
        (NS, "FunctionalExchangeRealization"),
    )
    realized_functional_exchanges = _descriptors.Allocation["FunctionalExchange"](
        "ownedFunctionalExchangeRealizations",
        (NS, "FunctionalExchangeRealization"),
        (NS, "FunctionalExchange"),
        attr="targetElement",
        backattr="sourceElement",
    )
    realizing_functional_exchanges = _descriptors.Backref["FunctionalExchange"](
        (NS, "FunctionalExchange"), "realized_functional_exchanges"
    )
    owner = _descriptors.Single["ComponentExchange"](
        _descriptors.Backref((NS, "ComponentExchange"), "allocated_functional_exchanges")
    )
    allocating_component_exchange = _descriptors.Alias["ComponentExchange"]("owner")
    categories = _descriptors.Backref["ExchangeCategory"](
        (NS, "ExchangeCategory"), "exchanges"
    )

    involving_functional_chains = _descriptors.Backref["FunctionalChain"](
        (NS, "FunctionalChain"), "involved_links"
    )

    if not t.TYPE_CHECKING:
        exchange_items = _descriptors.DeprecatedAccessor("exchanged_items")


class AbstractFunction(
    capellacore.Namespace,
    capellacore.InvolvedElement,
    information.AbstractInstance,
    AbstractFunctionalChainContainer,
    activity.CallBehaviorAction,
    behavior.AbstractEvent,
    abstract=True,
):
    """An abstract function."""

    _xmltag = "ownedFunctions"

    kind = _pods.EnumPOD("kind", FunctionKind)
    condition = _pods.StringPOD("condition")
    functions = _descriptors.Containment["AbstractFunction"](
        "ownedFunctions", (NS, "AbstractFunction")
    )
    function_realizations = _descriptors.Containment["FunctionRealization"](
        "ownedFunctionRealizations", (NS, "FunctionRealization")
    )
    realized_functions = _descriptors.Allocation["AbstractFunction"](
        "ownedFunctionRealizations",
        (NS, "FunctionRealization"),
        (NS, "AbstractFunction"),
        attr="targetElement",
        backattr="sourceElement",
    )
    realizing_functions = _descriptors.Backref["AbstractFunction"](
        (NS, "AbstractFunction"), "realized_functions", legacy_by_type=True
    )
    exchanges = _descriptors.Containment["FunctionalExchange"](
        "ownedFunctionalExchanges", (NS, "FunctionalExchange")
    )
    available_in_states = _descriptors.Association["capellacommon.State"](
        (ns.CAPELLACOMMON, "State"), "availableInStates"
    )

    related_exchanges = _descriptors.Backref["FunctionalExchange"](
        (NS, "FunctionalExchange"), "source.owner", "target.owner"
    )
    scenarios = _descriptors.Backref["interaction.Scenario"](
        (ns.INTERACTION, "Scenario"), "related_functions"
    )

    @property
    def is_leaf(self) -> bool:
        return not self.functions


class ComponentExchange(
    behavior.AbstractEvent,
    information.AbstractEventOperation,
    # NOTE: NamedElement comes before ExchangeSpecification in the upstream
    # metamodel, but that would result in an MRO conflict.
    ExchangeSpecification,
    capellacore.NamedElement,
    _AbstractExchange,
):
    _xmltag = "ownedComponentExchanges"

    kind = _pods.EnumPOD("kind", ComponentExchangeKind)
    is_oriented = _pods.BoolPOD("oriented")

    functional_exchange_allocations = _descriptors.Containment[
        "ComponentExchangeFunctionalExchangeAllocation"
    ](
        "ownedComponentExchangeFunctionalExchangeAllocations",
        (NS, "ComponentExchangeFunctionalExchangeAllocation"),
    )
    allocated_functional_exchanges = _descriptors.Allocation["FunctionalExchange"](
        "ownedComponentExchangeFunctionalExchangeAllocations",
        (NS, "ComponentExchangeFunctionalExchangeAllocation"),
        (NS, "FunctionalExchange"),
        attr="targetElement",
        backattr="sourceElement",
    )
    component_exchange_realizations = _descriptors.Containment[
        "ComponentExchangeRealization"
    ](
        "ownedComponentExchangeRealizations",
        (NS, "ComponentExchangeRealization"),
    )
    realized_component_exchanges = _descriptors.Allocation["ComponentExchange"](
        "ownedComponentExchangeRealizations",
        (NS, "ComponentExchangeRealization"),
        (NS, "ComponentExchange"),
        attr="targetElement",
        backattr="sourceElement",
    )
    realizing_component_exchanges = _descriptors.Backref["ComponentExchange"](
        (NS, "ComponentExchange"), "realized_component_exchanges"
    )
    ends = _descriptors.Containment["ComponentExchangeEnd"](
        "ownedComponentExchangeEnds", (NS, "ComponentExchangeEnd")
    )
    categories = _descriptors.Backref["ComponentExchangeCategory"](
        (NS, "ComponentExchangeCategory"), "exchanges"
    )

    allocating_physical_links = _descriptors.Backref["cs.PhysicalLink"](
        (ns.CS, "PhysicalLink"), "allocated_component_exchanges"
    )
    allocating_physical_paths = _descriptors.Backref["cs.PhysicalPath"](
        (ns.CS, "PhysicalPath"), "allocated_component_exchanges"
    )

    @property
    @deprecated(
        (
            "ComponentExchange.allocating_physical_link is deprecated,"
            " because it only takes into account the first allocation link."
            " Use allocating_physical_links instead, which allows multiple links."
        ),
        category=FutureWarning,
    )
    def allocating_physical_link(self) -> cs.PhysicalLink | None:
        links = self.allocating_physical_links
        return links[0] if links else None

    @property
    @deprecated(
        (
            "ComponentExchange.owner is deprecated,"
            " because it only takes into account the first allocation link."
            " Use allocating_physical_links instead, which allows multiple links."
        ),
        category=FutureWarning,
    )
    def owner(self) -> cs.PhysicalLink | None:
        links = self.allocating_physical_links
        return links[0] if links else None

    @property
    def exchange_items(
        self,
    ) -> _obj.ElementList[modellingcore.AbstractExchangeItem]:
        return (
            self.convoyed_informations
            + self.allocated_functional_exchanges.map("exchanged_items")
        )

    if not t.TYPE_CHECKING:
        allocated_exchange_items = _descriptors.DeprecatedAccessor(
            "convoyed_informations"
        )


class ComponentExchangeAllocation(capellacore.Allocation):
    pass


class ComponentExchangeAllocator(capellacore.NamedElement, abstract=True):
    component_exchange_allocations = _descriptors.Containment[
        "ComponentExchangeAllocation"
    ]("ownedComponentExchangeAllocations", (NS, "ComponentExchangeAllocation"))
    allocated_component_exchanges = _descriptors.Allocation["ComponentExchange"](
        "ownedComponentExchangeAllocations",
        (NS, "ComponentExchangeAllocation"),
        (NS, "ComponentExchange"),
        attr="targetElement",
        backattr="sourceElement",
    )


class ComponentExchangeCategory(capellacore.NamedElement):
    _xmltag = "ownedComponentExchangeCategories"

    exchanges = _descriptors.Association["ComponentExchange"](
        (NS, "ComponentExchange"), "exchanges"
    )


class ComponentExchangeEnd(
    modellingcore.InformationsExchanger, capellacore.CapellaElement
):
    port = _descriptors.Single["information.Port"](
        _descriptors.Association((ns.INFORMATION, "Port"), "port")
    )
    part = _descriptors.Single["cs.Part"](_descriptors.Association((ns.CS, "Part"), "part"))


class ComponentExchangeFunctionalExchangeAllocation(
    AbstractFunctionAllocation
):
    pass


class ComponentExchangeRealization(ExchangeSpecificationRealization):
    pass


class ComponentPort(
    information.Port, modellingcore.InformationsExchanger, information.Property
):
    """A component port."""

    _xmltag = "ownedFeatures"

    orientation = _pods.EnumPOD("orientation", OrientationPortKind)
    kind = _pods.EnumPOD("kind", ComponentPortKind)
    exchanges = _descriptors.Backref["ComponentExchange"](
        (NS, "ComponentExchange"), "source", "target"
    )

    if not t.TYPE_CHECKING:
        direction = _descriptors.DeprecatedAccessor("orientation")
        owner = _descriptors.DeprecatedAccessor("parent")


class ComponentPortAllocation(capellacore.Allocation):
    ends = _descriptors.Containment["ComponentPortAllocationEnd"](
        "ownedComponentPortAllocationEnds", (NS, "ComponentPortAllocationEnd")
    )


class ComponentPortAllocationEnd(capellacore.CapellaElement):
    port = _descriptors.Single["information.Port"](
        _descriptors.Association((ns.INFORMATION, "Port"), "port")
    )
    part = _descriptors.Single["cs.Part"](_descriptors.Association((ns.CS, "Part"), "part"))


class ReferenceHierarchyContext(modellingcore.ModelElement, abstract=True):
    source_reference_hierarchy = _descriptors.Association["FunctionalChainReference"](
        (NS, "FunctionalChainReference"), "sourceReferenceHierarchy"
    )
    target_reference_hierarchy = _descriptors.Association["FunctionalChainReference"](
        (NS, "FunctionalChainReference"), "targetReferenceHierarchy"
    )


class FunctionalChainInvolvementLink(
    FunctionalChainInvolvement, ReferenceHierarchyContext
):
    exchange_context = _descriptors.Single["capellacore.Constraint"](
        _descriptors.Association((ns.CAPELLACORE, "Constraint"), "exchangeContext")
    )
    exchanged_items = _descriptors.Association["information.ExchangeItem"](
        (ns.INFORMATION, "ExchangeItem"), "exchangedItems"
    )
    source = _descriptors.Single["FunctionalChainInvolvementFunction"](
        _descriptors.Association((NS, "FunctionalChainInvolvementFunction"), "source")
    )
    target = _descriptors.Single["FunctionalChainInvolvementFunction"](
        _descriptors.Association((NS, "FunctionalChainInvolvementFunction"), "target")
    )

    if not t.TYPE_CHECKING:
        context = _descriptors.DeprecatedAccessor("exchange_context")


class SequenceLink(capellacore.CapellaElement, ReferenceHierarchyContext):
    condition = _descriptors.Single["capellacore.Constraint"](
        _descriptors.Association((ns.CAPELLACORE, "Constraint"), "condition")
    )
    links = _descriptors.Association["FunctionalChainInvolvementLink"](
        (NS, "FunctionalChainInvolvementLink"), "links"
    )
    source = _descriptors.Single["SequenceLinkEnd"](
        _descriptors.Association((NS, "SequenceLinkEnd"), "source")
    )
    target = _descriptors.Single["SequenceLinkEnd"](
        _descriptors.Association((NS, "SequenceLinkEnd"), "target")
    )


class SequenceLinkEnd(capellacore.CapellaElement, abstract=True):
    pass


class FunctionalChainInvolvementFunction(
    FunctionalChainInvolvement, SequenceLinkEnd
):
    pass


class ControlNode(SequenceLinkEnd):
    _xmltag = "ownedSequenceNodes"

    kind = _pods.EnumPOD("kind", ControlNodeKind)


if not t.TYPE_CHECKING:

    def __getattr__(attr):
        if attr == "AbstractExchange":
            warnings.warn(
                (
                    "AbstractExchange is deprecated and will be removed soon,"
                    " use the concrete FunctionalExchange or ComponentExchange"
                    " class or another common superclass instead"
                ),
                DeprecationWarning,
                stacklevel=2,
            )
            return _AbstractExchange

        if attr == "Function":
            warnings.warn(
                "Function has been merged into AbstractFunction",
                DeprecationWarning,
                stacklevel=2,
            )
            return AbstractFunction

        raise AttributeError(f"{__name__} has no attribute {attr}")


from . import capellacommon, cs, interaction  # noqa: F401
