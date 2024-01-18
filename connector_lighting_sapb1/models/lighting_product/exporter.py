# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class LightingSAPB1ProductBatchDirectExporter(Component):
    """Export Lighting Products.

    For every product in the list, import it directly.
    """

    _name = "lighting.sapb1.product.batch.direct.exporter"
    _inherit = "connector.extension.generic.batch.direct.exporter"

    _apply_on = "lighting.sapb1.product"


class LightingSAPB1ProductBatchDelayedExporter(Component):
    """Export Lighting Products.

    For every product in the list, a delayed job is created.
    """

    _name = "lighting.sapb1.product.batch.delayed.exporter"
    _inherit = "connector.extension.generic.batch.delayed.exporter"

    _apply_on = "lighting.sapb1.product"


class LightingSAPB1ProductExporter(Component):
    _name = "lighting.sapb1.product.record.direct.exporter"
    _inherit = "lighting.sapb1.record.direct.exporter"

    _apply_on = "lighting.sapb1.product"

    def _has_to_skip(self, relation):
        """Return True if the export can be skipped"""
        return relation.state != "published"
