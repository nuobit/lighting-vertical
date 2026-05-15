# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductSparepart(models.Model):
    _name = "lighting.product.sparepart"
    _description = "Lighting Product Spare Part"
    _order = "sequence, id"

    product_id = fields.Many2one(
        comodel_name="lighting.product",
        string="Product",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    description = fields.Char()
