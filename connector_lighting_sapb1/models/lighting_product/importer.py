# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class LightingSAPB1ProductBatchDirectImporter(Component):
    """Import the SAP B1 Lighting Products.

    For every product in the list, import it directly.
    """

    _name = "lighting.sapb1.product.batch.direct.importer"
    _inherit = "connector.extension.generic.batch.direct.importer"

    _apply_on = "lighting.sapb1.product"


class LightingSAPB1ProductBatchDelayedImporter(Component):
    """Import the SAP B1 Lighting Products.

    For every product in the list, a delayed job is created.
    """

    _name = "lighting.sapb1.product.batch.delayed.importer"
    _inherit = "connector.extension.generic.batch.delayed.importer"

    _apply_on = "lighting.sapb1.product"


class LightingSAPB1ProductImporter(Component):
    _name = "lighting.sapb1.product.record.direct.importer"
    _inherit = "lighting.sapb1.record.direct.importer"

    _apply_on = "lighting.sapb1.product"
