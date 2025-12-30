# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
"""Common namespace definitions for the Capella metamodel."""

from capellambse.model import _obj

MODELLINGCORE = _obj.NS
METADATA = _obj.NS_METADATA

ACTIVITY = _obj.Namespace(
    "http://www.polarsys.org/capella/common/activity/{VERSION}",
    "org.polarsys.capella.common.data.activity",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
BEHAVIOR = _obj.Namespace(
    "http://www.polarsys.org/capella/common/behavior/{VERSION}",
    "org.polarsys.capella.common.data.behavior",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
CAPELLACOMMON = _obj.Namespace(
    "http://www.polarsys.org/capella/core/common/{VERSION}",
    "org.polarsys.capella.core.data.capellacommon",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
CAPELLACORE = _obj.Namespace(
    "http://www.polarsys.org/capella/core/core/{VERSION}",
    "org.polarsys.capella.core.data.capellacore",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
CAPELLAMODELLER = _obj.Namespace(
    "http://www.polarsys.org/capella/core/modeller/{VERSION}",
    "org.polarsys.capella.core.data.capellamodeller",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
CS = _obj.Namespace(
    "http://www.polarsys.org/capella/core/cs/{VERSION}",
    "org.polarsys.capella.core.data.cs",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
EPBS = _obj.Namespace(
    "http://www.polarsys.org/capella/core/epbs/{VERSION}",
    "org.polarsys.capella.core.data.epbs",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
FA = _obj.Namespace(
    "http://www.polarsys.org/capella/core/fa/{VERSION}",
    "org.polarsys.capella.core.data.fa",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
INFORMATION = _obj.Namespace(
    "http://www.polarsys.org/capella/core/information/{VERSION}",
    "org.polarsys.capella.core.data.information",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
INFORMATION_COMMUNICATION = _obj.Namespace(
    "http://www.polarsys.org/capella/core/information/communication/{VERSION}",
    "org.polarsys.capella.core.data.information.communication",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
INFORMATION_DATATYPE = _obj.Namespace(
    "http://www.polarsys.org/capella/core/information/datatype/{VERSION}",
    "org.polarsys.capella.core.data.information.datatype",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
INFORMATION_DATAVALUE = _obj.Namespace(
    "http://www.polarsys.org/capella/core/information/datavalue/{VERSION}",
    "org.polarsys.capella.core.data.information.datavalue",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
INTERACTION = _obj.Namespace(
    "http://www.polarsys.org/capella/core/interaction/{VERSION}",
    "org.polarsys.capella.core.data.interaction",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
LA = _obj.Namespace(
    "http://www.polarsys.org/capella/core/la/{VERSION}",
    "org.polarsys.capella.core.data.la",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
LIBRARIES = _obj.Namespace(
    "http://www.polarsys.org/capella/common/libraries/{VERSION}",
    "libraries",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
OA = _obj.Namespace(
    "http://www.polarsys.org/capella/core/oa/{VERSION}",
    "org.polarsys.capella.core.data.oa",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
PA = _obj.Namespace(
    "http://www.polarsys.org/capella/core/pa/{VERSION}",
    "org.polarsys.capella.core.data.pa",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
PA_DEPLOYMENT = _obj.Namespace(
    "http://www.polarsys.org/capella/core/pa/deployment/{VERSION}",
    "org.polarsys.capella.core.data.pa.deployment",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
RE = _obj.Namespace(
    "http://www.polarsys.org/capella/common/re/{VERSION}",
    "re",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
SA = _obj.Namespace(
    "http://www.polarsys.org/capella/core/ctx/{VERSION}",
    "org.polarsys.capella.core.data.ctx",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
SHARED_MODEL = _obj.Namespace(
    "http://www.polarsys.org/capella/core/sharedmodel/{VERSION}",
    "org.polarsys.capella.core.data.sharedmodel",
    _obj.CORE_VIEWPOINT,
    "7.0.0",
)
