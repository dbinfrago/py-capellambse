# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
"""Static duck-typing assertions checked by mypy."""

from __future__ import annotations

from capellambse import model
from capellambse.extensions import pvmt, validation


def protocol_ModelObject_compliance() -> None:
    mobj: model.ModelObject

    mobj = model.ModelElement()  # type: ignore[call-arg]
    mobj = model._descriptors._Specification()  # type: ignore[call-arg]
    mobj = model.diagram.Diagram()
    mobj = pvmt.ObjectPVMT()
    mobj = validation.ElementValidation()
    mobj = validation.LayerValidation()

    del mobj
