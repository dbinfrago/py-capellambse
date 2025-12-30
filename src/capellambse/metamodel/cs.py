# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
"""Implementation of objects and relations for Functional Analysis."""

from __future__ import annotations

import typing as t
import warnings

from lxml import etree

import capellambse.model as m
from capellambse.model import _descriptors, _obj, _pods

from . import capellacore, fa, information, modellingcore
from . import namespaces as ns

NS = ns.CS


class BlockArchitecturePkg(
    capellacore.ModellingArchitecturePkg, abstract=True
):
    """Container package for BlockArchitecture elements."""


class BlockArchitecture(fa.AbstractFunctionalArchitecture, abstract=True):
    """Parent class for deriving specific architectures for each design phase.

    Formerly known as BaseArchitectureLayer.
    """

    capability_pkg = _descriptors.Single["capellacommon.AbstractCapabilityPkg"](
        _descriptors.Containment(
            "ownedAbstractCapabilityPkg",
            (ns.CAPELLACOMMON, "AbstractCapabilityPkg"),
        )
    )
    interface_pkg = _descriptors.Single["InterfacePkg"](
        _descriptors.Containment("ownedInterfacePkg", (NS, "InterfacePkg"))
    )
    data_pkg = _descriptors.Single["information.DataPkg"](
        _descriptors.Containment("ownedDataPkg", (ns.INFORMATION, "DataPkg"))
    )

    @property
    def all_classes(self) -> _obj.ElementList[information.Class]:
        return self._model.search((ns.INFORMATION, "Class"), below=self)

    @property
    def all_collections(self) -> _obj.ElementList[information.Collection]:
        return self._model.search((ns.INFORMATION, "Collection"), below=self)

    @property
    def all_unions(self) -> _obj.ElementList[information.Union]:
        return self._model.search((ns.INFORMATION, "Union"), below=self)

    @property
    def all_enumerations(
        self,
    ) -> _obj.ElementList[information.datatype.Enumeration]:
        return self._model.search(
            (ns.INFORMATION_DATATYPE, "Enumeration"), below=self
        )

    @property
    def all_complex_values(
        self,
    ) -> _obj.ElementList[information.datavalue.AbstractComplexValue]:
        return self._model.search(
            (ns.INFORMATION_DATAVALUE, "AbstractComplexValue"), below=self
        )

    @property
    def all_interfaces(self) -> _obj.ElementList[Interface]:
        return self._model.search((NS, "Interface"), below=self)

    @property
    def all_capabilities(
        self,
    ) -> _obj.ElementList[interaction.AbstractCapability]:
        return self._model.search(
            (ns.INTERACTION, "AbstractCapability"), below=self
        )

    if not t.TYPE_CHECKING:
        capability_package = _descriptors.DeprecatedAccessor("capability_pkg")
        interface_package = _descriptors.DeprecatedAccessor("interface_pkg")
        data_package = _descriptors.DeprecatedAccessor("data_pkg")


class Block(
    fa.AbstractFunctionalBlock,
    # NOTE: In the upstream metamodel, ModellingBlock comes first,
    # but this would result in an MRO conflict.
    capellacore.ModellingBlock,
    abstract=True,
):
    """A modular unit that describes the structure of a system or element."""

    capability_pkg = _descriptors.Single["capellacommon.AbstractCapabilityPkg"](
        _descriptors.Containment(
            "ownedAbstractCapabilityPkg",
            (ns.CAPELLACOMMON, "AbstractCapabilityPkg"),
        )
    )
    interface_pkg = _descriptors.Single["InterfacePkg"](
        _descriptors.Containment("ownedInterfacePkg", (NS, "InterfacePkg"))
    )
    data_pkg = _descriptors.Single["information.DataPkg"](
        _descriptors.Containment("ownedDataPkg", (ns.INFORMATION, "DataPkg"))
    )
    state_machines = _descriptors.Containment["capellacommon.StateMachine"](
        "ownedStateMachines", (ns.CAPELLACOMMON, "StateMachine")
    )

    if not t.TYPE_CHECKING:
        interface_package = _descriptors.DeprecatedAccessor("interface_pkg")
        data_package = _descriptors.DeprecatedAccessor("data_pkg")


class ComponentArchitecture(BlockArchitecture, abstract=True):
    """A specialized kind of BlockArchitecture.

    Serves as a parent class for the various architecture levels, from
    System analysis down to EPBS architecture.
    """


class InterfaceAllocator(capellacore.CapellaElement, abstract=True):
    interface_allocations = _descriptors.Containment["InterfaceAllocation"](
        "ownedInterfaceAllocations", (NS, "InterfaceAllocation")
    )
    allocated_interfaces = _descriptors.Allocation["Interface"](
        "ownedInterfaceAllocations",
        (NS, "InterfaceAllocation"),
        (NS, "Interface"),
        attr="targetElement",
        backattr="sourceElement",
    )


class Component(
    Block,
    capellacore.Classifier,
    InterfaceAllocator,
    information.communication.CommunicationLinkExchanger,
    abstract=True,
):
    """An entity, with discrete structure within the system.

    Interacts with other Components of the system, thereby contributing
    at its lowest level to the system properties and characteristics.
    """

    is_actor = _pods.BoolPOD("actor")
    """Indicates if the Component is an Actor."""
    is_human = _pods.BoolPOD("human")
    """Indicates whether the Component is a Human."""
    interface_uses = _descriptors.Containment["InterfaceUse"](
        "ownedInterfaceUses", (NS, "InterfaceUse")
    )
    used_interfaces = _descriptors.Allocation["Interface"](
        "ownedInterfaceUses",
        (NS, "InterfaceUse"),
        (NS, "Interface"),
        attr="usedInterface",
    )
    interface_implementations = _descriptors.Containment["InterfaceImplementation"](
        "ownedInterfaceImplementations", (NS, "InterfaceImplementation")
    )
    implemented_interfaces = _descriptors.Allocation["Interface"](
        "ownedInterfaceImplementations",
        (NS, "InterfaceImplementation"),
        (NS, "Interface"),
        attr="implementedInterfaces",
    )
    component_realizations = _descriptors.Containment["ComponentRealization"](
        "ownedComponentRealizations", (NS, "ComponentRealization")
    )
    realized_components = _descriptors.Allocation["Component"](
        "ownedComponentRealizations",
        (NS, "ComponentRealization"),
        (NS, "Component"),
        attr="targetElement",
        backattr="sourceElement",
    )
    realizing_components = _descriptors.Backref["Component"](
        (NS, "Component"), "realized_components"
    )
    ports = _descriptors.Filter["fa.ComponentPort"](
        "owned_features", (ns.FA, "ComponentPort")
    )
    physical_ports = _descriptors.Filter["PhysicalPort"](
        "owned_features", (NS, "PhysicalPort")
    )
    owned_parts = _descriptors.Filter["Part"]("owned_features", (NS, "Part"))
    representing_parts = _descriptors.Backref["Part"]((NS, "Part"), "type")
    physical_paths = _descriptors.Containment["PhysicalPath"](
        "ownedPhysicalPath", (NS, "PhysicalPath")
    )
    physical_links = _descriptors.Containment["PhysicalLink"](
        "ownedPhysicalLinks", (NS, "PhysicalLink")
    )
    physical_link_categories = _descriptors.Containment["PhysicalLinkCategory"](
        "ownedPhysicalLinkCategories", (NS, "PhysicalLinkCategory")
    )
    related_exchanges = _descriptors.Backref["fa.ComponentExchange"](
        (ns.FA, "ComponentExchange"),
        "source",
        "source.owner",
        "target",
        "target.owner",
    )

    if not t.TYPE_CHECKING:
        owner = _descriptors.DeprecatedAccessor("parent")
        exchanges = _descriptors.DeprecatedAccessor("component_exchanges")
        parts = _descriptors.DeprecatedAccessor("representing_parts")

    def __init__(
        self,
        model: m.MelodyModel,
        parent: etree._Element,
        xmltag: str | None,
        /,
        create_part: bool = True,
        **kw: t.Any,
    ) -> None:
        super().__init__(model, parent, **kw)

        if create_part:
            if isinstance(self.parent, Component | ComponentPkg):
                self.parent.owned_parts.create(name=self.name, type=self)
            else:
                self.owned_parts.create(name=self.name, type=self)


class DeployableElement(capellacore.NamedElement, abstract=True):
    """A physical model element intended to be deployed."""


class DeploymentTarget(capellacore.NamedElement, abstract=True):
    """The physical target that will host a deployable element."""


class AbstractPathInvolvedElement(capellacore.InvolvedElement, abstract=True):
    pass


class Part(
    information.AbstractInstance,
    modellingcore.InformationsExchanger,
    DeployableElement,
    DeploymentTarget,
    AbstractPathInvolvedElement,
):
    """A representation of a physical component.

    In SysML, a Part is an owned property of a Block.
    """

    _xmltag = "ownedParts"

    deployment_links = _descriptors.Containment["AbstractDeploymentLink"](
        "ownedDeploymentLinks", (NS, "AbstractDeploymentLink")
    )
    deployed_parts = _descriptors.Allocation["DeployableElement"](
        "ownedDeploymentLinks",
        (NS, "AbstractDeploymentLink"),
        (NS, "DeployableElement"),
        attr="deployedElement",
        backattr="location",
    )
    owned_type = _descriptors.Single["modellingcore.AbstractType"](
        _descriptors.Containment("ownedAbstractType", (ns.MODELLINGCORE, "AbstractType"))
    )


class ArchitectureAllocation(capellacore.Allocation, abstract=True):
    pass


class ComponentRealization(capellacore.Allocation):
    """A realization that links to a component."""

    _xmltag = "ownedComponentRealizations"


class InterfacePkg(
    information.communication.MessageReferencePkg,
    capellacore.AbstractDependenciesPkg,
    capellacore.AbstractExchangeItemPkg,
):
    """A container for Interface elements."""

    interfaces = _descriptors.Containment["Interface"](
        "ownedInterfaces", (NS, "Interface")
    )
    packages = _descriptors.Containment["InterfacePkg"](
        "ownedInterfacePkgs", (NS, "InterfacePkg")
    )


class Interface(capellacore.GeneralClass, InterfaceAllocator):
    """An interface.

    An interface is a kind of classifier that represents a declaration of a set
    of coherent public features and obligations. An interface specifies a
    contract; any instance of a classifier that realizes the interface must
    fulfill that contract.

    Interfaces are defined by functional and physical characteristics that
    exist at a common boundary with co-functioning items and allow systems,
    equipment, software, and system data to be compatible.

    That design feature of one piece of equipment that affects a design feature
    of another piece of equipment. An interface can extend beyond the physical
    boundary between two items. (For example, the weight and center of gravity
    of one item can affect the interfacing item; however, the center of gravity
    is rarely located at the physical boundary. An electrical interface
    generally extends to the first isolating element rather than terminating at
    a series of connector pins.)

    Usage guideline
    ---------------
    In Capella, Interfaces are created to declare the nature of interactions
    between the System and external actors.
    """

    mechanism = _pods.StringPOD("mechanism")
    is_structural = _pods.BoolPOD("structural")
    exchange_item_allocations = _descriptors.Containment["ExchangeItemAllocation"](
        "ownedExchangeItemAllocations", (NS, "ExchangeItemAllocation")
    )
    allocated_exchange_items = _descriptors.Allocation["information.ExchangeItem"](
        "ownedExchangeItemAllocations",
        (NS, "ExchangeItemAllocation"),
        (ns.INFORMATION, "ExchangeItem"),
        attr="allocatedItem",
    )


class InterfaceImplementation(capellacore.Relationship):
    implemented_interface = _descriptors.Single["Interface"](
        _descriptors.Association((NS, "Interface"), "implementedInterface")
    )


class InterfaceUse(capellacore.Relationship):
    used_interface = _descriptors.Single["Interface"](
        _descriptors.Association((NS, "Interface"), "usedInterface")
    )


class ProvidedInterfaceLink(capellacore.Relationship, abstract=True):
    interface = _descriptors.Single["Interface"](
        _descriptors.Association((NS, "Interface"), "interface")
    )


class RequiredInterfaceLink(capellacore.Relationship, abstract=True):
    interface = _descriptors.Single["Interface"](
        _descriptors.Association((NS, "Interface"), "interface")
    )


class InterfaceAllocation(capellacore.Allocation, abstract=True):
    pass


class ExchangeItemAllocation(
    capellacore.Relationship,
    information.AbstractEventOperation,
    modellingcore.FinalizableElement,
):
    """An allocation of an ExchangeItem to an Interface."""

    send_protocol = _pods.EnumPOD(
        "sendProtocol", information.communication.CommunicationLinkProtocol
    )
    receive_protocol = _pods.EnumPOD(
        "receiveProtocol", information.communication.CommunicationLinkProtocol
    )
    allocated_item = _descriptors.Single["information.ExchangeItem"](
        _descriptors.Association((ns.INFORMATION, "ExchangeItem"), "allocatedItem")
    )

    if not t.TYPE_CHECKING:
        item = _descriptors.DeprecatedAccessor("allocated_item")


class AbstractDeploymentLink(capellacore.Relationship, abstract=True):
    deployed_element = _descriptors.Single["DeployableElement"](
        _descriptors.Association((NS, "DeployableElement"), "deployedElement")
    )
    location = _descriptors.Single["DeploymentTarget"](
        _descriptors.Association((NS, "DeploymentTarget"), "location")
    )


class AbstractPhysicalArtifact(capellacore.CapellaElement, abstract=True):
    pass


class AbstractPhysicalLinkEnd(capellacore.CapellaElement, abstract=True):
    pass


class AbstractPhysicalPathLink(fa.ComponentExchangeAllocator, abstract=True):
    pass


class PhysicalLink(
    AbstractPhysicalPathLink,
    AbstractPhysicalArtifact,
    AbstractPathInvolvedElement,
):
    ends = _descriptors.Association["AbstractPhysicalLinkEnd"](
        (NS, "AbstractPhysicalLinkEnd"), "linkEnds", fixed_length=2
    )
    functional_exchange_allocations = _descriptors.Containment[
        "fa.ComponentExchangeFunctionalExchangeAllocation"
    ](
        "ownedComponentExchangeFunctionalExchangeAllocations",
        (ns.FA, "ComponentExchangeFunctionalExchangeAllocation"),
    )
    allocated_functional_exchanges = _descriptors.Allocation["fa.FunctionalExchange"](
        "ownedComponentExchangeFunctionalExchangeAllocations",
        (ns.FA, "ComponentExchangeFunctionalExchangeAllocation"),
        (ns.FA, "FunctionalExchange"),
        attr="targetElement",
        backattr="sourceElement",
    )
    physical_link_ends = _descriptors.Containment["PhysicalLinkEnd"](
        "ownedPhysicalLinkEnds", (NS, "PhysicalLinkEnd")
    )
    physical_link_realizations = _descriptors.Containment["PhysicalLinkRealization"](
        "ownedPhysicalLinkRealizations", (NS, "PhysicalLinkRealization")
    )
    realized_physical_links = _descriptors.Allocation["PhysicalLink"](
        "ownedPhysicalLinkRealizations",
        (NS, "PhysicalLinkRealization"),
        (NS, "PhysicalLink"),
        attr="targetElement",
        backattr="sourceElement",
    )
    physical_paths = _descriptors.Backref["PhysicalPath"](
        (NS, "PhysicalPath"), "involved_items"
    )

    @property
    def source(self) -> AbstractPhysicalLinkEnd | None:
        try:
            return self.ends[0]
        except IndexError:
            return None

    @source.setter
    def source(self, end: AbstractPhysicalLinkEnd | None) -> None:
        if end is None:
            raise TypeError(f"Cannot delete 'source' of {type(self).__name__}")

        ends = self.ends
        if len(ends) == 0:
            ends.append(end)
        else:
            ends[0] = end

    @property
    def target(self) -> AbstractPhysicalLinkEnd | None:
        try:
            return self.ends[1]
        except IndexError:
            return None

    @target.setter
    def target(self, end: AbstractPhysicalLinkEnd | None) -> None:
        if end is None:
            raise TypeError(f"Cannot delete 'target' of {type(self).__name__}")

        ends = self.ends
        if len(ends) == 0:
            raise TypeError(
                f"Cannot set 'target' on a {type(self).__name__}"
                " that has no 'source'"
            )
        if len(ends) == 1:
            ends.append(end)
        else:
            ends[1] = end

    def links(self) -> _obj.ElementList[m.ModelElement]:
        warnings.warn(
            "PhysicalLink.links is deprecated and will be removed soon",
            category=FutureWarning,
            stacklevel=2,
        )
        return _obj.ElementList(self._model, [])

    if not t.TYPE_CHECKING:
        exchanges = _descriptors.DeprecatedAccessor("allocated_component_exchanges")
        owner = _descriptors.DeprecatedAccessor("parent")


class PhysicalLinkCategory(capellacore.NamedElement):
    links = _descriptors.Association["PhysicalLink"]((NS, "PhysicalLink"), "links")


class PhysicalLinkEnd(AbstractPhysicalLinkEnd):
    port = _descriptors.Single["PhysicalPort"](
        _descriptors.Association((NS, "PhysicalPort"), "port")
    )
    part = _descriptors.Single["Part"](_descriptors.Association((NS, "Part"), "part"))


class PhysicalLinkRealization(capellacore.Allocation):
    pass


class PhysicalPath(
    fa.ComponentExchangeAllocator,
    AbstractPathInvolvedElement,
    capellacore.InvolverElement,
    capellacore.NamedElement,
):
    """A physical path."""

    _xmltag = "ownedPhysicalPath"

    _involved_links = _descriptors.Association["AbstractPhysicalPathLink"](
        (NS, "AbstractPhysicalPathLink"), "involvedLinks"
    )
    physical_path_involvements = _descriptors.Containment["PhysicalPathInvolvement"](
        "ownedPhysicalPathInvolvements", (NS, "PhysicalPathInvolvement")
    )
    involved_items = _descriptors.Allocation["AbstractPathInvolvedElement"](
        "ownedPhysicalPathInvolvements",
        (NS, "PhysicalPathInvolvement"),
        (NS, "AbstractPathInvolvedElement"),
        attr="involved",
        legacy_by_type=True,
    )
    physical_path_realizations = _descriptors.Containment["PhysicalPathRealization"](
        "ownedPhysicalPathRealizations", (NS, "PhysicalPathRealization")
    )
    realized_paths = _descriptors.Allocation["PhysicalPath"](
        "ownedPhysicalPathRealizations",
        (NS, "PhysicalPathRealization"),
        (NS, "PhysicalPath"),
        attr="targetElement",
        backattr="sourceElement",
    )
    involved_links = _descriptors.Filter["PhysicalLink"](
        "involved_items", (NS, "PhysicalLink")
    )

    if not t.TYPE_CHECKING:
        exchanges = _descriptors.DeprecatedAccessor("allocated_component_exchanges")


class PhysicalPathInvolvement(capellacore.Involvement):
    next_involvements = _descriptors.Association["PhysicalPathInvolvement"](
        (NS, "PhysicalPathInvolvement"), "nextInvolvements"
    )


class PhysicalPathReference(PhysicalPathInvolvement):
    pass


class PhysicalPathRealization(capellacore.Allocation):
    pass


class PhysicalPort(
    information.Port,
    AbstractPhysicalArtifact,
    modellingcore.InformationsExchanger,
    AbstractPhysicalLinkEnd,
    information.Property,
):
    """A port on a physical component."""

    _xmltag = "ownedFeatures"

    component_port_allocations = _descriptors.Containment["fa.ComponentPortAllocation"](
        "ownedComponentPortAllocations",
        (ns.FA, "ComponentPortAllocation"),
    )
    allocated_component_ports = _descriptors.Allocation["fa.ComponentPort"](
        "ownedComponentPortAllocations",
        (ns.FA, "ComponentPortAllocation"),
        (ns.FA, "ComponentPort"),
        attr="targetElement",
        backattr="sourceElement",
    )
    physical_port_realizations = _descriptors.Containment["PhysicalPortRealization"](
        "ownedPhysicalPortRealizations", (NS, "PhysicalPortRealization")
    )
    realized_ports = _descriptors.Allocation["PhysicalPort"](
        "ownedPhysicalPortRealizations",
        (NS, "PhysicalPortRealization"),
        (NS, "PhysicalPort"),
        attr="targetElement",
        backattr="sourceElement",
    )
    links = _descriptors.Backref["PhysicalLink"]((NS, "PhysicalLink"), "ends")

    if not t.TYPE_CHECKING:
        owner = _descriptors.DeprecatedAccessor("parent")


class PhysicalPortRealization(capellacore.Allocation):
    pass


class ComponentPkg(capellacore.Structure, abstract=True):
    """A package containing parts."""

    parts = _descriptors.Containment["Part"]("ownedParts", (NS, "Part"))
    owned_parts = _descriptors.Alias["_obj.ElementList[Part]"]("parts")
    exchanges = _descriptors.Containment["fa.ComponentExchange"](
        "ownedComponentExchanges", (ns.FA, "ComponentExchange")
    )
    exchange_categories = _descriptors.Containment["fa.ComponentExchangeCategory"](
        "ownedComponentExchangeCategories",
        (ns.FA, "ComponentExchangeCategory"),
    )
    functional_links = _descriptors.Containment["fa.ExchangeLink"](
        "ownedFunctionalLinks", (ns.FA, "ExchangeLink")
    )
    functional_allocations = _descriptors.Containment["fa.ComponentFunctionalAllocation"](
        "ownedFunctionalAllocations",
        (ns.FA, "ComponentFunctionalAllocation"),
    )
    allocated_functions = _descriptors.Allocation["fa.AbstractFunction"](
        "ownedFunctionalAllocations",
        (ns.FA, "ComponentFunctionalAllocation"),
        (ns.FA, "AbstractFunction"),
        attr="targetElement",
        backattr="sourceElement",
    )
    component_exchange_realizations = _descriptors.Containment[
        "fa.ComponentExchangeRealization"
    ](
        "ownedComponentExchangeRealizations",
        (ns.FA, "ComponentExchangeRealization"),
    )
    realized_component_exchanges = _descriptors.Allocation["fa.ComponentExchange"](
        "ownedComponentExchangeRealizations",
        (ns.FA, "ComponentExchangeRealization"),
        (ns.FA, "ComponentExchange"),
        attr="targetElement",
        backattr="sourceElement",
    )
    physical_links = _descriptors.Containment["PhysicalLink"](
        "ownedPhysicalLinks", (NS, "PhysicalLink")
    )
    physical_link_categories = _descriptors.Containment["PhysicalLinkCategory"](
        "ownedPhysicalLinkCategories", (NS, "PhysicalLinkCategory")
    )
    state_machines = _descriptors.Containment["capellacommon.StateMachine"](
        "ownedStateMachines", (ns.CAPELLACOMMON, "StateMachine")
    )


from . import capellacommon, interaction  # noqa: F401
