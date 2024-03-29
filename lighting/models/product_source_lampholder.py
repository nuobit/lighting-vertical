# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductSourceLampholder(models.Model):
    _name = "lighting.product.source.lampholder"
    _description = "Product Source Lampholder"
    _rec_name = "code"
    _order = "code"

    code = fields.Char(
        required=True,
    )
    name = fields.Char(
        string="Description",
        translate=True,
    )
    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
    )

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env["lighting.product"].search_count(
                [
                    "|",
                    ("source_ids.lampholder_id", "=", record.id),
                    ("source_ids.lampholder_technical_id", "=", record.id),
                ]
            )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The lampholder name must be unique!"),
        ("code_uniq", "unique (code)", "The lampholder code must be unique!"),
    ]
