# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
"""Tools for the Operational Analysis layer."""

from __future__ import annotations

import sys
import typing as t
import warnings

import capellambse.model as m
from capellambse.model import _descriptors, _obj, _pods, diagram

from . import (
    activity,
    capellacommon,
    capellacore,
    cs,
    fa,
    information,
    interaction,
    modellingcore,
)
from . import namespaces as ns

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

NS = ns.OA


class OperationalAnalysis(cs.BlockArchitecture):
    """Provides access to the OperationalAnalysis layer of the model."""

    role_pkg = _descriptors.Containment["RolePkg"]("ownedRolePkg", (NS, "RolePkg"))
    entity_pkg = _descriptors.Single["EntityPkg"](
        _descriptors.Containment("ownedEntityPkg", (NS, "EntityPkg"))
    )
    concept_pkg = _descriptors.Containment["ConceptPkg"](
        "ownedConceptPkg", (NS, "ConceptPkg")
    )

    activity_pkg = _descriptors.Alias["OperationalActivityPkg"]("function_pkg")

    @property
    def all_activities(self) -> _obj.ElementList[OperationalActivity]:
        return self._model.search((NS, "OperationalActivity"), below=self)

    @property
    def all_processes(self) -> _obj.ElementList[OperationalProcess]:
        return self._model.search((NS, "OperationalProcess"), below=self)

    @property
    def all_actors(self) -> _obj.ElementList[Entity]:
        return self._model.search((NS, "Entity")).by_is_actor(True)

    @property
    def all_entities(self) -> _obj.ElementList[Entity]:
        return self._model.search((NS, "Entity"), below=self)

    @property
    def all_activity_exchanges(self) -> _obj.ElementList[fa.FunctionalExchange]:
        return self._model.search((ns.FA, "FunctionalExchange"), below=self)

    @property
    def all_entity_exchanges(self) -> _obj.ElementList[CommunicationMean]:
        return self._model.search((NS, "CommunicationMean"), below=self)

    @property
    def all_operational_processes(self) -> _obj.ElementList[OperationalProcess]:
        return self._model.search(OperationalProcess, below=self)

    @property
    @deprecated(
        (
            "OperationalActivity.root_activity can only handle a single"
            " OperationalActivity, use .activity_pkg.activities directly instead"
        ),
        category=FutureWarning,
    )
    def root_activity(self) -> OperationalActivity:
        pkg = self.activity_pkg
        if pkg is None:
            raise m.BrokenModelError(
                "OperationalAnalysis has no root ActivityPkg"
            )
        assert isinstance(pkg, OperationalActivityPkg)
        candidates = pkg.activities
        if len(candidates) < 1:
            raise m.BrokenModelError(
                "ActivityPkg does not contain any Activities"
            )
        if len(candidates) > 1:
            raise RuntimeError(
                "Expected 1 object for OperationalAnalysis.root_activity,"
                f" got {len(candidates)}"
            )
        return candidates[0]

    @property
    @deprecated(
        (
            "OperationalActivity.root_entity can only handle a single"
            " Entity, use .entity_pkg.entities directly instead"
        ),
        category=FutureWarning,
    )
    def root_entity(self) -> Entity:
        pkg = self.entity_pkg
        if pkg is None:
            raise m.BrokenModelError(
                "OperationalAnalysis has no root EntityPkg"
            )
        candidates = pkg.entities
        if len(candidates) < 1:
            raise m.BrokenModelError("Root EntityPkg is empty")
        if len(candidates) > 1:
            raise RuntimeError(
                "Expected 1 object for OperationalAnalysis.root_entity,"
                f" got {len(candidates)}"
            )
        return candidates[0]

    diagrams = diagram.DiagramAccessor(
        "Operational Analysis", cacheattr="_MelodyModel__diagram_cache"
    )

    if not t.TYPE_CHECKING:
        entity_package = _descriptors.DeprecatedAccessor("entity_pkg")
        activity_package = _descriptors.DeprecatedAccessor("activity_pkg")
        capability_package = _descriptors.DeprecatedAccessor("capability_pkg")


class OperationalScenario(capellacore.NamedElement, abstract=True):
    context = _pods.StringPOD("context")
    objective = _pods.StringPOD("objective")


class OperationalActivityPkg(fa.FunctionPkg):
    _xmltag = "ownedFunctionPkg"

    activities = _descriptors.Containment["OperationalActivity"](
        "ownedOperationalActivities", (NS, "OperationalActivity")
    )
    packages = _descriptors.Containment["OperationalActivityPkg"](
        "ownedOperationalActivityPkgs", (NS, "OperationalActivityPkg")
    )
    owner = _descriptors.Single["Entity"](_descriptors.Backref((NS, "Entity"), "activities"))


class OperationalActivity(fa.AbstractFunction):
    _xmltag = "ownedOperationalActivities"

    packages = _descriptors.Containment["OperationalActivityPkg"](
        "ownedOperationalActivityPkgs", (NS, "OperationalActivityPkg")
    )
    activities = _descriptors.Alias["_obj.ElementList[OperationalActivity]"]("functions")
    inputs = _descriptors.Backref["fa.FunctionalExchange"](  # type: ignore[assignment]
        (ns.FA, "FunctionalExchange"), "target"
    )
    outputs = _descriptors.Backref["fa.FunctionalExchange"](  # type: ignore[assignment]
        (ns.FA, "FunctionalExchange"), "source"
    )
    realizing_system_functions = _descriptors.Backref["sa.SystemFunction"](
        (ns.SA, "SystemFunction"), "realized_operational_activities"
    )

    owner = _descriptors.Single["Entity"](_descriptors.Backref((NS, "Entity"), "activities"))

    related_exchanges = _descriptors.Backref[fa.FunctionalExchange](
        (ns.FA, "FunctionalExchange"), "source", "target"
    )


class OperationalProcess(fa.FunctionalChain):
    pass


class Swimlane(capellacore.NamedElement, activity.ActivityPartition):
    pass


class OperationalCapabilityPkg(capellacommon.AbstractCapabilityPkg):
    _xmltag = "ownedAbstractCapabilityPkg"

    capabilities = _descriptors.Containment["OperationalCapability"](
        "ownedOperationalCapabilities", (NS, "OperationalCapability")
    )
    packages = _descriptors.Containment["OperationalCapabilityPkg"](
        "ownedOperationalCapabilityPkgs", (NS, "OperationalCapabilityPkg")
    )
    capability_configurations = _descriptors.Containment["CapabilityConfiguration"](
        "ownedCapabilityConfigurations", (NS, "CapabilityConfiguration")
    )
    concept_compliances = _descriptors.Containment["ConceptCompliance"](
        "ownedConceptCompliances", (NS, "ConceptCompliance")
    )
    complies_with_concepts = _descriptors.Allocation["Concept"](
        "ownedConceptCompliances",
        (NS, "ConceptCompliance"),
        (NS, "Concept"),
        attr="complyWithConcept",
        backattr="compliantCapability",
    )


class OperationalCapability(
    interaction.AbstractCapability, capellacore.Namespace
):
    """A capability in the OperationalAnalysis layer."""

    _xmltag = "ownedOperationalCapabilities"

    compliances = _descriptors.Association["ConceptCompliance"](
        (NS, "ConceptCompliance"), "compliances"
    )
    configurations = _descriptors.Association["CapabilityConfiguration"](
        (NS, "CapabilityConfiguration"), "configurations"
    )
    entity_involvements = _descriptors.Containment[
        "EntityOperationalCapabilityInvolvement"
    ](
        "ownedEntityOperationalCapabilityInvolvements",
        (NS, "EntityOperationalCapabilityInvolvement"),
    )
    involved_entities = _descriptors.Allocation["Entity"](
        "ownedEntityOperationalCapabilityInvolvements",
        (NS, "EntityOperationalCapabilityInvolvement"),
        (NS, "Entity"),
        attr="involved",
        legacy_by_type=True,
    )
    involved_activities = _descriptors.Alias["_obj.ElementList[OperationalActivity]"](
        "involved_functions"
    )
    involved_processes = _descriptors.Alias["_obj.ElementList[OperationalProcess]"](
        "involved_chains"
    )
    owned_processes = _descriptors.Alias["_obj.ElementList[OperationalProcess]"](
        "functional_chains"
    )


class ActivityAllocation(capellacore.Allocation):
    pass


class RolePkg(capellacore.Structure):
    packages = _descriptors.Containment["RolePkg"]("ownedRolePkgs", (NS, "RolePkg"))
    roles = _descriptors.Containment["Role"]("ownedRoles", (NS, "Role"))


class Role(information.AbstractInstance):
    assembly_usages = _descriptors.Containment["RoleAssemblyUsage"](
        "ownedRoleAssemblyUsages", (NS, "RoleAssemblyUsage")
    )
    activity_allocations = _descriptors.Containment["ActivityAllocation"](
        "ownedActivityAllocations", (NS, "ActivityAllocation")
    )


class RoleAssemblyUsage(capellacore.NamedElement):
    child = _descriptors.Association["Role"]((NS, "Role"), "child")


class RoleAllocation(capellacore.Allocation):
    pass


class EntityPkg(cs.ComponentPkg):
    _xmltag = "ownedEntityPkg"

    entities = _descriptors.Containment["Entity"]("ownedEntities", (NS, "Entity"))
    packages = _descriptors.Containment["EntityPkg"]("ownedEntityPkgs", (NS, "EntityPkg"))
    locations = _descriptors.Containment["Location"]("ownedLocations", (NS, "Location"))
    communication_means = _descriptors.Alias["_obj.ElementList[CommunicationMean]"](
        "exchanges"
    )


class AbstractConceptItem(cs.Component, abstract=True):
    composing_links = _descriptors.Association["ItemInConcept"](
        (NS, "ItemInConcept"), "composingLinks"
    )


class Entity(
    AbstractConceptItem,
    modellingcore.InformationsExchanger,
    capellacore.InvolvedElement,
):
    """An Entity in the OperationalAnalysis layer."""

    _xmltag = "ownedEntities"

    organisational_unit_memberships = _descriptors.Association[
        "OrganisationalUnitComposition"
    ]((NS, "OrganisationalUnitComposition"), "organisationalUnitMemberships")
    actual_location = _descriptors.Association["Location"](
        (NS, "Location"), "actualLocation"
    )
    entities = _descriptors.Containment["Entity"]("ownedEntities", (NS, "Entity"))
    communication_means = _descriptors.Containment["CommunicationMean"](
        "ownedCommunicationMeans", (NS, "CommunicationMean")
    )
    exchanges = _descriptors.Alias["_obj.ElementList[CommunicationMean]"](
        "communication_means"
    )
    activities = _descriptors.Allocation["OperationalActivity"](
        "ownedFunctionalAllocation",
        (ns.FA, "ComponentFunctionalAllocation"),
        (NS, "OperationalActivity"),
        attr="targetElement",
        backattr="sourceElement",
    )
    capabilities = _descriptors.Backref["OperationalCapability"](
        (NS, "OperationalCapability"), "involved_entities"
    )
    related_exchanges = _descriptors.Backref["CommunicationMean"](
        (NS, "CommunicationMean"), "source", "target"
    )
    realizing_system_components = _descriptors.Backref["sa.SystemComponent"](
        (ns.SA, "SystemComponent"), "realized_operational_entities"
    )

    @property
    def inputs(self) -> _obj.ElementList[CommunicationMean]:
        return self._model.search((NS, "CommunicationMean")).by_target(self)

    @property
    def outputs(self) -> _obj.ElementList[CommunicationMean]:
        return self._model.search((NS, "CommunicationMean")).by_source(self)


class ConceptPkg(capellacore.Structure):
    packages = _descriptors.Containment["ConceptPkg"](
        "ownedConceptPkgs", (NS, "ConceptPkg")
    )
    concepts = _descriptors.Containment["Concept"]("ownedConcepts", (NS, "Concept"))


class Concept(capellacore.NamedElement):
    compliances = _descriptors.Association["ConceptCompliance"](
        (NS, "ConceptCompliance"), "compliances"
    )
    composite_links = _descriptors.Containment["ItemInConcept"](
        "compositeLinks", (NS, "ItemInConcept")
    )


class ConceptCompliance(capellacore.Relationship):
    comply_with_concept = _descriptors.Single["Concept"](
        _descriptors.Association((NS, "Concept"), "complyWithConcept")
    )
    compliant_capability = _descriptors.Single["OperationalCapability"](
        _descriptors.Association((NS, "OperationalCapability"), "compliantCapability")
    )


class ItemInConcept(capellacore.NamedElement):
    concept = _descriptors.Single["Concept"](_descriptors.Association((NS, "Concept"), "concept"))
    item = _descriptors.Single["AbstractConceptItem"](
        _descriptors.Association((NS, "AbstractConceptItem"), "item")
    )


class CommunityOfInterest(capellacore.NamedElement):
    community_of_interest_compositions = _descriptors.Containment[
        "CommunityOfInterestComposition"
    ](
        "communityOfInterestCompositions",
        (NS, "CommunityOfInterestComposition"),
    )


class CommunityOfInterestComposition(capellacore.NamedElement):
    community_of_interest = _descriptors.Association["CommunityOfInterest"](
        (NS, "CommunityOfInterest"), "communityOfInterest"
    )
    interested_organisational_unit = _descriptors.Association["OrganisationalUnit"](
        (NS, "OrganisationalUnit"), "interestedOrganisationUnit"
    )


class OrganisationalUnit(capellacore.NamedElement):
    organisational_unit_compositions = _descriptors.Containment[
        "OrganisationalUnitComposition"
    ]("organisationalUnitCompositions", (NS, "OrganisationalUnitComposition"))
    community_of_interest_memberships = _descriptors.Association[
        "CommunityOfInterestComposition"
    ]((NS, "CommunityOfInterestComposition"), "communityOfInterestMemberships")


class OrganisationalUnitComposition(capellacore.NamedElement):
    organisational_unit = _descriptors.Association["OrganisationalUnit"](
        (NS, "OrganisationalUnit"), "organisationalUnit"
    )
    participating_entity = _descriptors.Association["Entity"](
        (NS, "Entity"), "participatingEntity"
    )


class Location(AbstractConceptItem):
    location_description = _pods.StringPOD("locationDescription")
    located_entities = _descriptors.Association["Entity"](
        (NS, "Entity"), "locatedEntities"
    )


class CapabilityConfiguration(AbstractConceptItem):
    configured_capability = _descriptors.Association["OperationalCapability"](
        (NS, "OperationalCapability"), "configuredCapability"
    )


# NOTE: CommunicationMean should directly inherit from NamedRelationship,
# however this would result in an MRO conflict that cannot be resolved.
# Therefore we only inherit from ComponentExchange, copy the only missing
# definition (naming_rules), and register it as virtual subclass.
class CommunicationMean(fa.ComponentExchange):
    """An operational entity exchange."""

    _xmltag = "ownedComponentExchanges"

    # Taken from NamedRelationship, see note above
    naming_rules = _descriptors.Containment["capellacore.NamingRule"](
        "namingRules", (ns.CAPELLACORE, "NamingRule")
    )

    allocated_interactions = _descriptors.Alias["_obj.ElementList[fa.FunctionalExchange]"](
        "allocated_functional_exchanges"
    )


capellacore.NamedRelationship.register(CommunicationMean)


class EntityOperationalCapabilityInvolvement(capellacore.Involvement):
    pass


if not t.TYPE_CHECKING:

    def __getattr__(name):
        if name == "AbstractEntity":
            warnings.warn(
                "AbstractEntity has been merged into Entity",
                DeprecationWarning,
                stacklevel=2,
            )
            return Entity
        raise AttributeError(name)


from . import sa  # noqa: F401
