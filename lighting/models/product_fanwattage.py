# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LightingProductFanWattage(models.Model):
    _name = "lighting.product.fanwattage"
    _rec_name = "wattage"

    wattage = fields.Float(string="Wattage (W)", required=True)

    product_id = fields.Many2one(
        comodel_name="lighting.product", ondelete="cascade", string="Product"
    )

    _sql_constraints = [
        (
            "wattage_product_uniq",
            "unique (product_id, wattage)",
            "There are duplicated wattages on the same product!",
        ),
    ]

    @api.constrains("wattage")
    def _check_wattage(self):
        for rec in self:
            if rec.wattage == 0:
                raise ValidationError("The fan wattage, if defined, cannot be 0")
