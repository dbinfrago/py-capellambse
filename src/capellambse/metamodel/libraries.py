# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
import enum

import capellambse.model as m
from capellambse.model import _descriptors, _obj, _pods

from . import namespaces as ns

NS = ns.LIBRARIES


@m.stringy_enum
@enum.unique
class AccessPolicy(enum.Enum):
    READ_ONLY = "readOnly"
    READ_AND_WRITE = "readAndWrite"


class LibraryAbstractElement(_obj.ModelElement, abstract=True):
    pass


class ModelInformation(LibraryAbstractElement):
    references = _descriptors.Containment["LibraryReference"](
        "ownedReferences", (NS, "LibraryReference")
    )
    version = _descriptors.Association["ModelVersion"]((NS, "ModelVersion"), "version")


class LibraryReference(LibraryAbstractElement):
    library = _descriptors.Single["ModelInformation"](
        _descriptors.Association((NS, "ModelInformation"), "library")
    )
    access_policy = _pods.EnumPOD("accessPolicy", AccessPolicy)
    version = _descriptors.Association["ModelVersion"]((NS, "ModelVersion"), "version")


class ModelVersion(LibraryAbstractElement):
    major_version_number = _pods.IntPOD("majorVersionNumber")
    minor_version_number = _pods.IntPOD("minorVersionNumber")
    last_modified_file_stamp = _pods.IntPOD("lastModifiedFileStamp")
