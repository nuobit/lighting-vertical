# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductPhotobiologicalRiskGroup(models.Model):
    _name = "lighting.product.photobiologicalriskgroup"
    _description = "Product Photobiological Risk Group"
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
        inverse_name="photobiological_risk_group_id",
        string="Products",
    )

    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec.product_ids)

    _sql_constraints = [
        (
            "name_uniq",
            "unique (name)",
            "The photobiological risk group description must be unique!",
        ),
    ]
