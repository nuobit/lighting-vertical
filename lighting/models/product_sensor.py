# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import UserError


class LightingProductSensor(models.Model):
    _name = "lighting.product.sensor"
    _description = "Product Sensor"
    _order = "name"

    name = fields.Char(
        string="Sensor",
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
                [("sensor_ids", "=", record.id)]
            )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The sensor must be unique!"),
    ]

    def unlink(self):
        if self.env["lighting.product"].search_count([("sensor_ids", "in", self.ids)]):
            raise UserError(
                _("You are trying to delete a record that is still referenced!")
            )
        return super().unlink()
