# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class LightingProductReview(models.Model):
    _name = "lighting.product.review"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "package_id,product_id"

    package_id = fields.Many2one(
        comodel_name="lighting.review.package",
        ondelete="restrict",
        required=True,
        tracking=True,
    )
    reviewed = fields.Boolean(
        tracking=True,
    )
    date = fields.Datetime(readonly=True, tracking=True, compute="_compute_date")

    @api.depends("reviewed")
    def _compute_date(self):
        for rec in self:
            if not rec.reviewed:
                rec.date = False
            else:
                rec.date = fields.Datetime.now()

    comment = fields.Text(
        tracking=True,
    )
    product_id = fields.Many2one(
        comodel_name="lighting.product",
        ondelete="cascade",
        required=True,
        tracking=True,
    )

    _sql_constraints = [
        (
            "uniq1",
            "unique (package_id,product_id)",
            "A package can only be used one time for each product!",
        ),
    ]

    # def write(self, values):
    #     if "reviewed" in values:
    #         if values["reviewed"]:
    #             values.update({"date": fields.Datetime.now()})
    #         else:
    #             values.update({"date": None})
    #     res = super().write(values)
    #     return res
