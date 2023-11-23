# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductConnectorType(models.Model):
    _name = "lighting.product.connectortype"
    _description = "Product Connector Type"
    _order = "name"

    name = fields.Char(
        string="Description",
        required=True,
    )
    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
    )
    product_ids = fields.One2many(
        comodel_name="lighting.product",
        inverse_name="charger_connector_type_id",
    )

    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec.product_ids)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The connector type must be unique!"),
    ]
