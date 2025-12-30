# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import capellambse.model as m
from capellambse.model import _descriptors

from .. import capellacore, cs
from .. import namespaces as ns

NS = ns.PA_DEPLOYMENT


class AbstractPhysicalInstance(capellacore.CapellaElement, abstract=True):
    pass


class ComponentInstance(
    AbstractPhysicalInstance,
    cs.DeployableElement,
    cs.DeploymentTarget,
):
    abstract_physical_instances = _descriptors.Containment["AbstractPhysicalInstance"](
        "ownedAbstractPhysicalInstances", (NS, "AbstractPhysicalInstance")
    )
    instance_deployment_links = _descriptors.Containment["InstanceDeploymentLink"](
        "ownedInstanceDeploymentLinks", (NS, "InstanceDeploymentLink")
    )
    type = _descriptors.Association["PhysicalComponent"](
        (NS, "PhysicalComponent"), "type"
    )


class ConnectionInstance(AbstractPhysicalInstance):
    connection_ends = _descriptors.Association["PortInstance"](
        (NS, "PortInstance"), "connectionEnds"
    )
    type = _descriptors.Association["fa.ComponentExchange"](
        (ns.FA, "ComponentExchange"), "type"
    )


class DeploymentAspect(capellacore.Structure):
    configurations = _descriptors.Containment["DeploymentConfiguration"](
        "ownedConfigurations", (NS, "DeploymentConfiguration")
    )
    deployment_aspects = _descriptors.Containment["DeploymentAspect"](
        "ownedDeploymentAspects", (NS, "DeploymentAspect")
    )


class DeploymentConfiguration(capellacore.NamedElement):
    deployment_links = _descriptors.Containment["cs.AbstractDeploymentLink"](
        "ownedDeploymentLinks", (ns.CS, "AbstractDeploymentLink")
    )
    physical_instances = _descriptors.Containment["AbstractPhysicalInstance"](
        "ownedPhysicalInstances", (NS, "AbstractPhysicalInstance")
    )


class InstanceDeploymentLink(cs.AbstractDeploymentLink):
    pass


class PartDeploymentLink(cs.AbstractDeploymentLink):
    pass


class PortInstance(AbstractPhysicalInstance):
    connections = _descriptors.Association["ConnectionInstance"](
        (NS, "ConnectionInstance"), "connections"
    )
    type = _descriptors.Association["fa.ComponentPort"]((ns.FA, "ComponentPort"), "type")


class TypeDeploymentLink(cs.AbstractDeploymentLink):
    pass


from .. import fa  # noqa: F401
from . import PhysicalComponent  # noqa: F401
