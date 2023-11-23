# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductLedChip(models.Model):
    _name = "lighting.product.ledchip"
    _description = "Product LED chip"
    _rec_name = "reference"
    _order = "source_line_id,date desc"

    reference = fields.Char()
    brand_id = fields.Many2one(
        comodel_name="lighting.product.ledbrand",
        ondelete="restrict",
        required=True,
    )
    date = fields.Date()
    source_line_id = fields.Many2one(
        comodel_name="lighting.product.source.line",
        ondelete="cascade",
    )

    _sql_constraints = [
        (
            "ledchip_uniq",
            "unique (source_line_id, date)",
            "The chip date must be unique!",
        ),
    ]
