# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


# Electrical characteristics tab
class LightingProductFrequency(models.Model):
    _name = "lighting.product.frequency"
    _description = "Product Frequency"
    _order = "name"

    name = fields.Char(
        string="Frequency",
        required=True,
        translate=True,
    )
    product_ids = fields.One2many(
        comodel_name="lighting.product",
        inverse_name="frequency_id",
    )
    product_count = fields.Integer(
        string="Product(s)",
        compute="_compute_product_count",
    )

    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec.product_ids)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The frequency must be unique!"),
    ]
