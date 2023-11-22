# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductModel(models.Model):
    _name = "lighting.product.model"

    name = fields.Char(string="Name", required=True)

    product_count = fields.Integer(
        compute="_compute_product_count", string="Product(s)"
    )

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env["lighting.product"].search_count(
                [("model_id", "=", record.id)]
            )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The model name must be unique!"),
    ]
