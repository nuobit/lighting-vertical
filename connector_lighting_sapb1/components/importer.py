# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class LightingSAPB1DirectImporter(AbstractComponent):
    """Base importer for Lighting SAP B1"""

    _name = "lighting.sapb1.record.direct.importer"
    _inherit = [
        "connector.extension.generic.record.direct.importer",
        "base.lighting.sapb1.connector",
    ]


class LightingSAPB1BatchImporter(AbstractComponent):
    """The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = "lighting.sapb1.batch.importer"
    _inherit = [
        "connector.extension.generic.batch.importer",
        "base.lighting.sapb1.connector",
    ]
