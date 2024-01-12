# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields

TOREVIEW_STRING = _("%s (to review)")
TOREVIEW_HELP = _("Enabled if the field value has not been validated yet")


def get_string(field_name):
    return TOREVIEW_STRING % _(field_name)


# I have to use Python inheritance, surprisingly it does not work with Odoo inheritance
class LightingReviewMixin:
    # to review layout
    def _compute_review_mode(self):
        for rec in self:
            rec.review_mode = self.env.user.review_mode

    review_mode = fields.Boolean(
        string="Review mode", compute="_compute_review_mode", default=False, store=False
    )

    def toggle_review_mode(self):
        self.ensure_one()
        self.env.user.review_mode = not self.env.user.review_mode

    # to review count
    @api.model
    def _get_toreview_fields(self):
        return {
            x
            for x, _ in filter(
                lambda x: x[1].type == "boolean" and x[0].startswith("toreview_"),
                self._fields.items(),
            )
        }

    @api.depends(_get_toreview_fields)
    def _compute_toreview_count(self):
        for rec in self:
            rec_vals = [getattr(rec, x) for x in rec._get_toreview_fields()]
            rec.toreview_count = len(list(filter(lambda x: x, rec_vals)))

    toreview_count = fields.Integer(compute="_compute_toreview_count", store=True)
