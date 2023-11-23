# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductEcorraeCategory(models.Model):
    _name = "lighting.product.ecorraecategory"
    _description = "Product EcoRrae Category"
    _order = "name"

    name = fields.Char(
        string="Description",
        required=True,
    )
    product_count = fields.Integer(
        compute="_compute_product_count", string="Product(s)"
    )
    product_ids = fields.One2many(
        comodel_name="lighting.product", inverse_name="ecorrae_category_id"
    )
    product2_ids = fields.One2many(
        comodel_name="lighting.product", inverse_name="ecorrae2_category_id"
    )

    def _compute_product_count(self):
        for rec in self:
            products = set(rec.product_ids.ids + rec.product2_ids.ids)
            rec.product_count = len(products)

    _sql_constraints = [
        (
            "name_uniq",
            "unique (name)",
            "The ecorrae category description must be unique!",
        ),
    ]
