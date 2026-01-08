# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
"""Tools for the EPBS layer."""

from __future__ import annotations

import enum

import capellambse.model as m
from capellambse.model import _descriptors, _obj, _pods, diagram

from . import capellacommon, capellacore, cs
from . import namespaces as ns

NS = ns.EPBS


@m.stringy_enum
@enum.unique
class ConfigurationItemKind(enum.Enum):
    UNSET = "Unset"
    COTSCI = "COTSCI"
    """Commercial Off The Shelves Configuration Item."""
    CSCI = "CSCI"
    """Computer Software Configuration Item."""
    HWCI = "HWCI"
    """Hardware Configuration Item."""
    INTERFACE_CI = "InterfaceCI"
    """Interface Configuration Item."""
    NDICI = "NDICI"
    """Non Developmental Configuration Item."""
    PRIME_ITEM_CI = "PrimeItemCI"
    """Prime Item Configuration Item."""
    SYSTEM_CI = "SystemCI"
    """System Configuration Item."""


class EPBSArchitecturePkg(cs.BlockArchitecturePkg):
    architectures = _descriptors.Containment["EPBSArchitecture"](
        "ownedEPBSArchitectures", (NS, "EPBSArchitecture")
    )


class EPBSArchitecture(cs.ComponentArchitecture):
    configuration_item_pkg = _descriptors.Single["ConfigurationItemPkg"](
        _descriptors.Containment(
            "ownedConfigurationItemPkg", (NS, "ConfigurationItemPkg")
        )
    )
    physical_architecture_realizations = _descriptors.Containment[
        "PhysicalArchitectureRealization"
    ](
        "ownedPhysicalArchitectureRealizations",
        (NS, "PhysicalArchitectureRealization"),
    )
    realized_physical_architecture = _descriptors.Single(
        _descriptors.Allocation["pa.PhysicalArchitecture"](
            "ownedPhysicalArchitectureRealizations",
            (NS, "PhysicalArchitectureRealization"),
            (ns.PA, "PhysicalArchitecture"),
            attr="targetElement",
            backattr="sourceElement",
        )
    )

    @property
    def all_configuration_items(self) -> _obj.ElementList[ConfigurationItem]:
        return self._model.search((NS, "ConfigurationItem"), below=self)

    diagrams = diagram.DiagramAccessor(
        "EPBS architecture", cacheattr="_MelodyModel__diagram_cache"
    )


class ConfigurationItemPkg(cs.ComponentPkg):
    configuration_items = _descriptors.Containment["ConfigurationItem"](
        "ownedConfigurationItems", (NS, "ConfigurationItem")
    )
    configuration_item_pkgs = _descriptors.Containment["ConfigurationItemPkg"](
        "ownedConfigurationItemPkgs", (NS, "ConfigurationItemPkg")
    )


class ConfigurationItem(
    capellacommon.CapabilityRealizationInvolvedElement, cs.Component
):
    identifier = _pods.StringPOD("itemIdentifier")
    kind = _pods.EnumPOD("kind", ConfigurationItemKind)
    configuration_items = _descriptors.Containment["ConfigurationItem"](
        "ownedConfigurationItems", (NS, "ConfigurationItem")
    )
    configuration_item_pkgs: _descriptors.Containment[ConfigurationItemPkg] = _descriptors.Containment["ConfigurationItemPkg"](
        "ownedConfigurationItemPkgs", (NS, "ConfigurationItemPkg")
    )
    physical_artifact_realizations = _descriptors.Containment[
        "PhysicalArtifactRealization"
    ]("ownedPhysicalArtifactRealizations", (NS, "PhysicalArtifactRealization"))
    realized_physical_artifacts = _descriptors.Allocation["cs.AbstractPhysicalArtifact"](
        "ownedPhysicalArtifactRealizations",
        (NS, "PhysicalArtifactRealization"),
        (ns.CS, "AbstractPhysicalArtifact"),
        attr="targetElement",
        backattr="sourceElement",
    )


class PhysicalArchitectureRealization(cs.ArchitectureAllocation):
    pass


class PhysicalArtifactRealization(capellacore.Allocation):
    pass


from . import la, pa  # noqa: F401
