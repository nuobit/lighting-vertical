# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProduct(models.Model):
    _inherit = "lighting.product"

    class_id = fields.Many2one(
        comodel_name="lighting.etim.class",
        ondelete="restrict",
    )
    feature_ids = fields.One2many(
        string="Features",
        comodel_name="lighting.etim.product.feature",
        inverse_name="product_id",
        copy=True,
    )
