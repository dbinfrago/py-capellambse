# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
"""Tools for the Logical Architecture layer."""

from __future__ import annotations

import sys
import typing as t

import capellambse.model as m
from capellambse.model import _descriptors, _obj, diagram

from . import capellacommon, cs, fa, interaction
from . import namespaces as ns

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

NS = ns.LA


class LogicalArchitecturePkg(cs.BlockArchitecturePkg):
    architectures = _descriptors.Containment["LogicalArchitecture"](
        "ownedLogicalArchitectures", (NS, "LogicalArchitecture")
    )


class LogicalArchitecture(cs.ComponentArchitecture):
    component_pkg = _descriptors.Single["LogicalComponentPkg"](
        _descriptors.Containment("ownedLogicalComponentPkg", (NS, "LogicalComponentPkg"))
    )
    system_analysis_realizations = _descriptors.Containment["SystemAnalysisRealization"](
        "ownedSystemAnalysisRealizations", (NS, "SystemAnalysisRealization")
    )
    realized_system_analysis = _descriptors.Allocation["sa.SystemAnalysis"](
        "ownedSystemAnalysisRealizations",
        (NS, "SystemAnalysisRealization"),
        (ns.SA, "SystemAnalysis"),
        attr="targetElement",
        backattr="sourceElement",
    )

    @property
    def root_function(self) -> LogicalFunction:
        """Returns the first function in the function_pkg."""
        pkg = self.function_pkg
        assert pkg is not None
        if not pkg.functions:
            raise RuntimeError(f"Package {pkg._short_repr_()} is empty")
        return pkg.functions[0]

    @property
    def root_component(self) -> LogicalComponent:
        assert self.component_pkg is not None
        return self.component_pkg.components.by_is_actor(False, single=True)

    @property
    def all_components(self) -> _obj.ElementList[LogicalComponent]:
        return self._model.search((NS, "LogicalComponent"), below=self)

    @property
    def all_actors(self) -> _obj.ElementList[LogicalComponent]:
        return self._model.search(LogicalComponent).by_is_actor(True)

    @property
    def all_actor_exchanges(self) -> _obj.ElementList[fa.ComponentExchange]:
        return self._model.search(
            (ns.FA, "ComponentExchange"), below=self
        ).filter(
            lambda e: (
                (
                    e.source is not None
                    and e.source.parent is not None
                    and e.source.parent.is_actor
                )
                or (
                    e.target is not None
                    and e.target.parent is not None
                    and e.target.parent.is_actor
                )
            )
        )

    @property
    def all_component_exchanges(self) -> _obj.ElementList[fa.ComponentExchange]:
        return self._model.search((ns.FA, "ComponentExchange"), below=self)

    @property
    @deprecated(
        (
            "LogicalArchitecture.component_exchanges will soon change"
            " to map the directly contained ComponentExchanges;"
            " use 'all_component_exchanges' to refer to"
            " all recursively contained exchanges instead"
        ),
        category=FutureWarning,
    )
    def component_exchanges(self) -> _obj.ElementList[fa.ComponentExchange]:  # type: ignore[override]
        return self.all_component_exchanges

    diagrams = diagram.DiagramAccessor(
        "Logical Architecture", cacheattr="_MelodyModel__diagram_cache"
    )

    if not t.TYPE_CHECKING:
        component_package = _descriptors.DeprecatedAccessor("component_pkg")
        actor_exchanges = _descriptors.DeprecatedAccessor("all_actor_exchanges")


class LogicalFunction(fa.AbstractFunction):
    functions = _descriptors.Containment["LogicalFunction"](
        "ownedFunctions", (NS, "LogicalFunction")
    )
    packages = _descriptors.Containment["LogicalFunctionPkg"](
        "ownedLogicalFunctionPkgs", (NS, "LogicalFunctionPkg")
    )
    realized_system_functions = _descriptors.Alias["_obj.ElementList[sa.SystemFunction]"](
        "realized_functions"
    )
    owner = _descriptors.Single["LogicalComponent"](
        _descriptors.Backref((NS, "LogicalComponent"), "allocated_functions")
    )
    involved_in = _descriptors.Backref["CapabilityRealization"](
        (NS, "CapabilityRealization"), "involved_functions"
    )
    realizing_physical_functions = _descriptors.Backref["pa.PhysicalFunction"](
        (ns.PA, "PhysicalFunction"), "realized_logical_functions"
    )


class LogicalFunctionPkg(fa.FunctionPkg):
    _xmltag = "ownedFunctionPkg"

    functions = _descriptors.Containment["LogicalFunction"](
        "ownedLogicalFunctions", (NS, "LogicalFunction")
    )
    packages = _descriptors.Containment["LogicalFunctionPkg"](
        "ownedLogicalFunctionPkgs", (NS, "LogicalFunctionPkg")
    )


class LogicalComponent(
    cs.Component, capellacommon.CapabilityRealizationInvolvedElement
):
    _xmltag = "ownedLogicalComponents"

    components = _descriptors.Containment["LogicalComponent"](
        "ownedLogicalComponents", (NS, "LogicalComponent")
    )
    architectures = _descriptors.Containment["LogicalArchitecture"](
        "ownedLogicalArchitectures", (NS, "LogicalArchitecture")
    )
    packages = _descriptors.Containment["LogicalComponentPkg"](
        "ownedLogicalComponentPkgs", (NS, "LogicalComponentPkg")
    )
    realized_system_components = _descriptors.Alias["_obj.ElementList[sa.SystemComponent]"](
        "realized_components"
    )
    realizing_physical_components = _descriptors.Backref["pa.PhysicalComponent"](
        (ns.PA, "PhysicalComponent"), "realized_logical_components"
    )


class LogicalComponentPkg(cs.ComponentPkg):
    _xmltag = "ownedLogicalComponentPkg"

    components = _descriptors.Containment["LogicalComponent"](
        "ownedLogicalComponents", (NS, "LogicalComponent")
    )
    packages = _descriptors.Containment["LogicalComponentPkg"](
        "ownedLogicalComponentPkgs", (NS, "LogicalComponentPkg")
    )


class CapabilityRealization(interaction.AbstractCapability):
    _xmltag = "ownedCapabilityRealizations"

    involved_functions = _descriptors.Allocation[LogicalFunction](
        None, None, (NS, "LogicalFunction")
    )
    capability_realization_involvements = _descriptors.Containment[
        "capellacommon.CapabilityRealizationInvolvement"
    ](
        "ownedCapabilityRealizationInvolvements",
        (ns.CAPELLACOMMON, "CapabilityRealizationInvolvement"),
    )
    involved_elements = _descriptors.Allocation[
        "capellacommon.CapabilityRealizationInvolvedElement"
    ](
        "ownedCapabilityRealizationInvolvements",
        (ns.CAPELLACOMMON, "CapabilityRealizationInvolvement"),
        (ns.CAPELLACOMMON, "CapabilityRealizationInvolvedElement"),
        attr="involved",
    )
    involved_components = _descriptors.Filter["LogicalComponent"](
        "involved_elements", (NS, "LogicalComponent"), legacy_by_type=True
    )

    if not t.TYPE_CHECKING:
        owned_chains = _descriptors.DeprecatedAccessor("functional_chains")


class CapabilityRealizationPkg(capellacommon.AbstractCapabilityPkg):
    """A capability package that can hold capabilities."""

    _xmltag = "ownedAbstractCapabilityPkg"

    capabilities = _descriptors.Containment["CapabilityRealization"](
        "ownedCapabilityRealizations", (NS, "CapabilityRealization")
    )
    packages = _descriptors.Containment["CapabilityRealizationPkg"](
        "ownedCapabilityRealizationPkgs", (NS, "CapabilityRealizationPkg")
    )


class SystemAnalysisRealization(cs.ArchitectureAllocation):
    pass


class ContextInterfaceRealization(cs.InterfaceAllocation):
    pass


from . import pa, sa  # noqa: F401
