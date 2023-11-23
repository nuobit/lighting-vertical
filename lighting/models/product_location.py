# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import UserError


class LightingProductLocation(models.Model):
    _name = "lighting.product.location"
    _description = "Product Location"
    _order = "name"

    name = fields.Char(
        required=True,
        translate=True,
    )
    # TODO: restrict len(code)=5
    code = fields.Char(
        required=True,
    )
    description_text = fields.Char(
        help="Text to show",
        translate=True,
    )
    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
    )

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env["lighting.product"].search_count(
                [("location_ids", "=", record.id)]
            )

    color = fields.Integer(
        string="Color Index",
    )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The location must be unique!"),
    ]

    def unlink(self):
        records = self.env["lighting.product"].search(
            [("location_ids", "in", self.ids)]
        )
        if records:
            raise UserError(
                _("You are trying to delete a record that is still referenced!")
            )
        return super().unlink()
