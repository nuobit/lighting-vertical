# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import UserError


class LightingProductDimmable(models.Model):
    _name = "lighting.product.dimmable"
    _description = "Product Dimmable"
    _order = "name"

    name = fields.Char(
        string="Dimmable",
        required=True,
        translate=True,
    )

    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
    )

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env["lighting.product"].search_count(
                [("dimmable_ids", "=", record.id)]
            )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The dimmable must be unique!"),
    ]

    def unlink(self):
        records = self.env["lighting.product"].search(
            [("dimmable_ids", "in", self.ids)]
        )
        if records:
            raise UserError(
                _("You are trying to delete a record that is still referenced!")
            )
        return super().unlink()
