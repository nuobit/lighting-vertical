# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductCategory(models.Model):
    _name = "lighting.product.category"
    _inherit = ["lighting.product.category", "lighting.seo.mixin"]

    seo_keyword_ids = fields.Many2many(
        relation="lighting_product_category_seo_keyword_rel",
        column1="category_id",
        column2="keyword_id",
    )
