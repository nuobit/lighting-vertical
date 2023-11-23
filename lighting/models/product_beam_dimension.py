# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductBeamDimension(models.Model):
    _name = "lighting.product.beam.dimension"
    _description = "Product Beam Dimension"
    _inherit = "lighting.product.dimension.abstract"

    beam_id = fields.Many2one(
        comodel_name="lighting.product.beam",
        ondelete="cascade",
    )
