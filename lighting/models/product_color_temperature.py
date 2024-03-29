# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import UserError


class LightingProductColorTemperature(models.Model):
    _name = "lighting.product.color.temperature"
    _description = "Product Color Temperature"
    _rec_name = "value"
    _order = "value"

    value = fields.Integer(
        required=True,
    )
    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
    )

    def _compute_product_count(self):
        for rec in self:
            rec.product_count = self.env["lighting.product"].search_count(
                [
                    (
                        "source_ids.line_ids.color_temperature_flux_ids.color_temperature_id",
                        "=",
                        rec.id,
                    )
                ]
            )

    _sql_constraints = [
        ("name_uniq", "unique (value)", "The color temperature must be unique!"),
    ]

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, "%iK" % rec.value))
        return res

    def unlink(self):
        records = self.env["lighting.product.source.line"].search(
            [("color_temperature_flux_ids.color_temperature_id", "in", self.ids)]
        )
        if records:
            raise UserError(
                _("You are trying to delete a record that is still referenced!")
            )
        return super().unlink()
