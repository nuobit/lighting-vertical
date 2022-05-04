# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)


class LightingProductExporter(Component):
    _name = 'sapb1.light.product.exporter'
    _inherit = 'sapb1.exporter'

    _apply_on = 'sapb1.light.product'

    def _has_to_skip(self):
        """ Return True if the export can be skipped """
        return self.binding.state != 'published'


class LightingProductDirectBatchExporter(Component):
    """ Export Odoo Products.

    For every product in the list, import it directly.
    """
    _name = 'sapb1.light.product.direct.batch.exporter'
    _inherit = 'sapb1.direct.batch.exporter'

    _apply_on = 'sapb1.light.product'


class LightingProductDelayedBatchExporter(Component):
    """ Export Odoo Products.

    For every product in the list, a delayed job is created.
    """
    _name = 'sapb1.light.product.delayed.batch.exporter'
    _inherit = 'sapb1.delayed.batch.exporter'

    _apply_on = 'sapb1.light.product'
