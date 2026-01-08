# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import enum

import capellambse.model as m
from capellambse.model import _descriptors, _obj, _pods

from . import namespaces as ns

NS = ns.RE


@m.stringy_enum
@enum.unique
class CatalogElementKind(enum.Enum):
    REC = "REC"
    RPL = "RPL"
    REC_RPL = "REC_RPL"
    GROUPING = "GROUPING"


class ReAbstractElement(_obj.ModelElement, abstract=True):
    pass


class ReNamedElement(ReAbstractElement, abstract=True):
    name = _pods.StringPOD("name")


class ReDescriptionElement(ReNamedElement, abstract=True):
    description = _pods.StringPOD("description")


class ReElementContainer(_obj.ModelElement, abstract=True):
    elements = _descriptors.Containment["CatalogElement"](
        "ownedElements", (NS, "CatalogElement")
    )


class CatalogElementPkg(ReNamedElement, ReElementContainer):
    element_pkgs = _descriptors.Containment["CatalogElementPkg"](
        "ownedElementPkgs", (NS, "CatalogElementPkg")
    )


class RecCatalog(CatalogElementPkg):
    compliancy_definition_pkg = _descriptors.Containment["CompliancyDefinitionPkg"](
        "ownedCompliancyDefinitionPkg", (NS, "CompliancyDefinitionPkg")
    )


class GroupingElementPkg(CatalogElementPkg):
    pass


class CatalogElementLink(ReAbstractElement):
    source = _descriptors.Association["CatalogElement"]((NS, "CatalogElement"), "source")
    target = _descriptors.Association["_obj.ModelElement"](
        (ns.MODELLINGCORE, "ModelElement"), "target"
    )
    origin = _descriptors.Association["CatalogElementLink"](
        (NS, "CatalogElementLink"), "origin"
    )
    unsynchronized_features = _pods.StringPOD("unsynchronizedFeatures")
    is_suffixed = _pods.BoolPOD("suffixed")


class CatalogElement(ReDescriptionElement, ReElementContainer):

    kind = _pods.EnumPOD("kind", CatalogElementKind)
    author = _pods.StringPOD("author")
    environment = _pods.StringPOD("environment")
    suffix = _pods.StringPOD("suffix")
    purpose = _pods.StringPOD("purpose")
    is_read_only = _pods.BoolPOD("readOnly")
    version = _pods.StringPOD("version")
    tags = _pods.StringPOD("tags")
    origin = _descriptors.Single(
        _descriptors.Association["CatalogElement"](
            (NS, "CatalogElement"), "origin"
        )
    )
    current_compliancy = _descriptors.Association["CompliancyDefinition"](
        (NS, "CompliancyDefinition"), "currentCompliancy"
    )
    default_replica_compliancy = _descriptors.Association["CompliancyDefinition"](
        (NS, "CompliancyDefinition"), "defaultReplicaCompliancy"
    )
    links = _descriptors.Containment["CatalogElementLink"](
        "ownedLinks", (NS, "CatalogElementLink")
    )


class CompliancyDefinitionPkg(ReNamedElement):
    definitions = _descriptors.Containment["CompliancyDefinition"](
        "ownedDefinitions", (NS, "CompliancyDefinition")
    )


class CompliancyDefinition(ReDescriptionElement):
    pass
