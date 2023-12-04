# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductApplication(models.Model):
    _name = "lighting.product.application"
    _inherit = ["lighting.product.application", "lighting.seo.mixin"]

    seo_keyword_ids = fields.Many2many(
        relation="lighting_product_application_seo_keyword_rel",
        column1="application_id",
        column2="keyword_id",
    )
