# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models

from . import mixin


class LightingProductSourceLine(models.Model, mixin.LightingReviewMixin):
    _inherit = "lighting.product.source.line"

    # to review fields
    toreview_cri_min = fields.Boolean(
        string=mixin.get_string("CRI"),
        help=mixin.TOREVIEW_HELP,
        track_visibility="onchange",
    )

    toreview_color_consistency = fields.Boolean(
        string=mixin.get_string("Color consistency (SDCM)"),
        help=mixin.TOREVIEW_HELP,
        track_visibility="onchange",
    )
