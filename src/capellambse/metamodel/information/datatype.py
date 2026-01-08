# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import enum
import typing as t

import capellambse.model as m
from capellambse.model import _descriptors, _pods

from .. import capellacore, modellingcore
from .. import namespaces as ns
from . import datavalue

NS = ns.INFORMATION_DATATYPE
NS_DV = ns.INFORMATION_DATAVALUE


@m.stringy_enum
@enum.unique
class NumericTypeKind(enum.Enum):
    """The kind of this numeric data type."""

    INTEGER = "INTEGER"
    FLOAT = "FLOAT"


class DataType(
    capellacore.GeneralizableElement,
    datavalue.DataValueContainer,
    modellingcore.FinalizableElement,
    abstract=True,
):
    _xmltag = "ownedDataTypes"

    is_discrete = _pods.BoolPOD("discrete")
    """Whether or not this data type characterizes a discrete value."""
    is_min_inclusive = _pods.BoolPOD("minInclusive")
    is_max_inclusive = _pods.BoolPOD("maxInclusive")
    pattern = _pods.StringPOD("pattern")
    """Textual specification of a constraint associated to this data type."""
    visibility = _pods.EnumPOD("visibility", capellacore.VisibilityKind)
    information_realizations = _descriptors.Containment["InformationRealization"](
        "ownedInformationRealizations",
        (ns.INFORMATION, "InformationRealization"),
    )

    if not t.TYPE_CHECKING:
        min_inclusive = _descriptors.DeprecatedAccessor("is_min_inclusive")
        max_inclusive = _descriptors.DeprecatedAccessor("is_max_inclusive")


class BooleanType(DataType):
    literals = _descriptors.Containment["datavalue.LiteralBooleanValue"](
        "ownedLiterals", (NS_DV, "LiteralBooleanValue"), fixed_length=2
    )
    default_value = _descriptors.Single["datavalue.AbstractBooleanValue"](
        _descriptors.Containment("ownedDefaultValue", (NS_DV, "AbstractBooleanValue"))
    )
    if not t.TYPE_CHECKING:
        default = _descriptors.DeprecatedAccessor("default_value")


class Enumeration(DataType):
    owned_literals = _descriptors.Containment["datavalue.EnumerationLiteral"](
        "ownedLiterals", (NS_DV, "EnumerationLiteral")
    )
    default_value = _descriptors.Single["datavalue.AbstractEnumerationValue"](
        _descriptors.Containment("ownedDefaultValue", (NS_DV, "AbstractEnumerationValue"))
    )
    null_value = _descriptors.Single["datavalue.AbstractEnumerationValue"](
        _descriptors.Containment("ownedNullValue", (NS_DV, "AbstractEnumerationValue"))
    )
    min_value = _descriptors.Single["datavalue.AbstractEnumerationValue"](
        _descriptors.Containment("ownedMinValue", (NS_DV, "AbstractEnumerationValue"))
    )
    max_value = _descriptors.Single["datavalue.AbstractEnumerationValue"](
        _descriptors.Containment("ownedMaxValue", (NS_DV, "AbstractEnumerationValue"))
    )
    domain_type = _descriptors.Single["DataType"](
        _descriptors.Association((NS, "DataType"), "domainType")
    )

    @property
    def literals(self) -> m.ElementList[datavalue.EnumerationLiteral]:
        """Return all owned and inherited literals."""
        return (
            self.owned_literals + self.super.literals
            if isinstance(self.super, Enumeration)
            else self.owned_literals
        )


class StringType(DataType):
    default_value = _descriptors.Single["datavalue.AbstractStringValue"](
        _descriptors.Containment("ownedDefaultValue", (NS_DV, "AbstractStringValue"))
    )
    null_value = _descriptors.Single["datavalue.AbstractStringValue"](
        _descriptors.Containment("ownedNullValue", (NS_DV, "AbstractStringValue"))
    )
    min_length = _descriptors.Single["datavalue.NumericValue"](
        _descriptors.Containment("ownedMinLength", (NS_DV, "NumericValue"))
    )
    max_length = _descriptors.Single["datavalue.NumericValue"](
        _descriptors.Containment("ownedMaxLength", (NS_DV, "NumericValue"))
    )


class NumericType(DataType):
    kind = _pods.EnumPOD("kind", NumericTypeKind)
    default_value = _descriptors.Single["datavalue.NumericValue"](
        _descriptors.Containment("ownedDefaultValue", (NS_DV, "NumericValue"))
    )
    null_value = _descriptors.Single["datavalue.NumericValue"](
        _descriptors.Containment("ownedNullValue", (NS_DV, "NumericValue"))
    )
    min_value = _descriptors.Single["datavalue.NumericValue"](
        _descriptors.Containment("ownedMinValue", (NS_DV, "NumericValue"))
    )
    max_value = _descriptors.Single["datavalue.NumericValue"](
        _descriptors.Containment("ownedMaxValue", (NS_DV, "NumericValue"))
    )


class PhysicalQuantity(NumericType):
    unit = _descriptors.Single["Unit"](_descriptors.Association((NS, "Unit"), "unit"))


from . import InformationRealization, Unit  # noqa: F401
