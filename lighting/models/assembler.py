# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingAssembler(models.Model):
    _name = "lighting.assembler"
    _description = "Assembler"
    _order = "name"

    name = fields.Char(
        string="Assembler",
        required=True,
    )
    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
    )

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env["lighting.product"].search_count(
                [("assembler_id", "=", record.id)]
            )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The assembler must be unique!"),
    ]
