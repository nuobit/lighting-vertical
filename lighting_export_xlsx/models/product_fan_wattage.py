# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class LightingProductFanWattage(models.Model):
    _inherit = "lighting.product.fanwattage"

    def export_xlsx(self, template_id=None):
        return ", ".join(["%g" % x.wattage for x in self])
