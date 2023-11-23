# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductRecessDimension(models.Model):
    _name = "lighting.product.recessdimension"
    _description = "Product Recess Dimension"
    _inherit = "lighting.product.dimension.abstract"

    product_id = fields.Many2one(
        comodel_name="lighting.product",
        ondelete="cascade",
    )
