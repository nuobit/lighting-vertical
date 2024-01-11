# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class LightingProductAbstractDimension(models.AbstractModel):
    _inherit = "lighting.product.dimension.abstract"

    def export_xlsx(self, template_id=None):
        if not self:
            return None

        res = {}
        for rec in self:
            res[rec.display_name] = rec.value

        return [res]
