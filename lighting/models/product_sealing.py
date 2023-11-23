# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import UserError


class LightingProductSealing(models.Model):
    _name = "lighting.product.sealing"
    _description = "Product Sealing"
    _order = "name"

    name = fields.Char(
        required=True,
    )
    product_ids = fields.One2many(
        comodel_name="lighting.product",
        inverse_name="sealing_id",
    )
    product2_ids = fields.One2many(
        comodel_name="lighting.product",
        inverse_name="sealing2_id",
    )
    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
    )

    def _compute_product_count(self):
        for rec in self:
            products = set(rec.product_ids.ids + rec.product2_ids.ids)
            rec.product_count = len(products)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The sealing must be unique!"),
    ]

    def unlink(self):
        if self.env["lighting.product"].search_count(
            ["|", ("sealing_id", "in", self.ids), ("sealing2_id", "in", self.ids)]
        ):
            raise UserError(
                _("You are trying to delete a record that is still referenced!")
            )
        return super().unlink()
