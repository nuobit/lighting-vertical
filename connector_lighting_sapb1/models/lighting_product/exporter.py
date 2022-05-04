# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class LightingProductExporter(Component):
    _name = 'sapb1.lighting.product.exporter'
    _inherit = 'sapb1.lighting.exporter'

    _apply_on = 'sapb1.lighting.product'

    def _has_to_skip(self):
        """ Return True if the export can be skipped """
        return self.binding.state != 'published'


class LightingProductDirectBatchExporter(Component):
    """ Export Odoo Products.

    For every product in the list, import it directly.
    """
    _name = 'sapb1.lighting.product.direct.batch.exporter'
    _inherit = 'sapb1.lighting.direct.batch.exporter'

    _apply_on = 'sapb1.lighting.product'


class LightingProductDelayedBatchExporter(Component):
    """ Export Odoo Products.

    For every product in the list, a delayed job is created.
    """
    _name = 'sapb1.lighting.product.delayed.batch.exporter'
    _inherit = 'sapb1.lighting.delayed.batch.exporter'

    _apply_on = 'sapb1.lighting.product'
