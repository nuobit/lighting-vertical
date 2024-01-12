# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models

from . import mixin


class LightingProductSourceLine(models.Model):
    _name = "lighting.product.source.line"
    _inherit = ["lighting.product.source.line", "lighting.review.mixin"]

    toreview_cri_min = fields.Boolean(
        string=mixin.get_string("CRI"),
        help=mixin.TOREVIEW_HELP,
        tracking=True,
    )
    toreview_color_consistency = fields.Boolean(
        string=mixin.get_string("Color consistency (SDCM)"),
        help=mixin.TOREVIEW_HELP,
        tracking=True,
    )
