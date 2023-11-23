# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LightingProductFanWattage(models.Model):
    _name = "lighting.product.fanwattage"
    _description = "Product Fan Wattage"
    _rec_name = "wattage"

    wattage = fields.Float(
        string="Wattage (W)",
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name="lighting.product",
        ondelete="cascade",
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
                raise ValidationError(_("The fan wattage, if defined, cannot be 0"))
