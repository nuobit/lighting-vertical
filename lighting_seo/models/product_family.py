# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models

MIN_STOCK = 10


class LightingProductFamily(models.Model):
    _name = "lighting.product.family"
    _inherit = ["lighting.product.family", "lighting.seo.mixin"]

    seo_keyword_ids = fields.Many2many(
        relation="lighting_product_family_seo_keyword_rel",
        column1="family_id",
        column2="keyword_id",
    )
