# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import UserError


class LightingEnergyEfficiency(models.Model):
    _name = "lighting.energyefficiency"
    _description = "Product Energy Efficiency"
    _order = "sequence"

    sequence = fields.Integer(
        required=True,
        default=1,
        help="The sequence field is used to define order",
    )
    name = fields.Char(
        string="Description",
        required=True,
    )

    color = fields.Integer(
        string="Color Index",
    )

    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
    )

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env["lighting.product"].search_count(
                [
                    ("source_ids.line_ids.efficiency_ids", "in", record.ids),
                ]
            )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The energy efficiency must be unique!"),
    ]

    def unlink(self):
        records = self.env["lighting.product.source.line"].search(
            [
                ("efficiency_ids", "in", self.ids),
            ]
        )
        if records:
            raise UserError(
                _(
                    "You are trying to delete a record that is still referenced by products %s"
                )
                % records.mapped("source_id.product_id.reference")
            )
        return super().unlink()
