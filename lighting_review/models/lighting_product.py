# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models

from . import mixin


class LightingProduct(models.Model, mixin.LightingReviewMixin):
    _inherit = "lighting.product"

    # TODO find this data autoamtically
    _toreview_related_models = ["source_ids.line_ids"]

    # review fields
    review_ids = fields.One2many(
        comodel_name="lighting.product.review",
        inverse_name="product_id",
        string="Reviews",
    )

    # to review layout
    def show_fields_toreview(self):
        # TODO show wizard with only the fields to review and
        #  be able to edit from there
        pass

    # to review count
    def _get_toreview_count_fields(self):
        return ["toreview_count"] + [
            "%s.toreview_count" % x for x in self._toreview_related_models
        ]

    @api.depends(_get_toreview_count_fields)
    def _compute_toreview_fields_count(self):
        for rec in self:
            rec.toreview_fields_count = sum(
                [sum(rec.mapped(f)) for f in rec._get_toreview_count_fields()]
            )

    toreview_fields_count = fields.Integer(
        string="To review", compute="_compute_toreview_fields_count", store=True
    )

    # to review fields
    toreview_lifetime = fields.Boolean(
        string=mixin.get_string("Lifetime (h)"),
        help=mixin.TOREVIEW_HELP,
        track_visibility="onchange",
    )

    toreview_led_lifetime_l = fields.Boolean(
        string=mixin.get_string("LED lifetime L"),
        help=mixin.TOREVIEW_HELP,
        track_visibility="onchange",
    )

    toreview_led_lifetime_b = fields.Boolean(
        string=mixin.get_string("LED lifetime B"),
        help=mixin.TOREVIEW_HELP,
        track_visibility="onchange",
    )
    toreview_dimmable_ids = fields.Boolean(
        string=mixin.get_string("Dimmables"),
        help=mixin.TOREVIEW_HELP,
        track_visibility="onchange",
    )
    toreview_input_voltage_id = fields.Boolean(
        string=mixin.get_string("Input voltage"),
        help=mixin.TOREVIEW_HELP,
        track_visibility="onchange",
    )
