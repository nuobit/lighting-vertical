# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingCatalog(models.Model):
    _name = "lighting.catalog"
    _inherit = ["lighting.catalog", "lighting.seo.mixin"]

    seo_keyword_ids = fields.Many2many(
        relation="lighting_catalog_seo_keyword_rel",
        column1="catalog_id",
        column2="keyword_id",
    )
