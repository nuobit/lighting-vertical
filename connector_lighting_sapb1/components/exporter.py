# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class LightingSAPB1RecordDirectExporter(AbstractComponent):
    """Base Exporter for SAP B1 Lighting"""

    _name = "lighting.sapb1.record.direct.exporter"
    _inherit = [
        "connector.extension.generic.record.direct.exporter",
        "base.lighting.sapb1.connector",
    ]


class LightingSAPB1BatchExporter(AbstractComponent):
    """The role of a BatchExporter is to search for a list of
    items to export, then it can either export them directly or delay
    the export of each item separately.
    """

    _name = "lighting.sapb1.batch.exporter"
    _inherit = [
        "connector.extension.generic.batch.exporter",
        "base.lighting.sapb1.connector",
    ]
