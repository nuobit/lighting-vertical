# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingAttachment(models.Model):
    _inherit = "lighting.attachment"

    use_as_product_datasheet = fields.Boolean(
        default=False,
    )
