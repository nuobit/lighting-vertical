# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import datetime

from odoo import _, api, fields, models


class LightingProductReview(models.Model):
    _name = "lighting.review.package"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _order = "name"

    name = fields.Char(
        required=True,
        tracking=True,
    )
    description = fields.Text(
        tracking=True,
    )
    start_date = fields.Date(
        required=True,
        tracking=True,
    )
    due_date = fields.Date(
        required=True,
        help="Maximum completion date",
        tracking=True,
    )
    end_date = fields.Date(
        help="Actual completion date",
        tracking=True,
    )
    responsible_ids = fields.Many2many(
        comodel_name="res.users",
        relation="lighting_review_package_user_rel",
        string="Responsibles",
        required=True,
        tracking=True,
    )
    review_ids = fields.One2many(
        comodel_name="lighting.product.review",
        inverse_name="package_id",
        string="Reviews",
        copy=True,
        tracking=True,
    )
    product_count = fields.Integer(
        string="Product(s)",
        compute="_compute_product_count",
    )

    @api.depends("review_ids")
    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec.review_ids)

    reviewed_count = fields.Integer(
        string="Reviewed product(s)",
        compute="_compute_reviewed_count",
    )
    pending_count = fields.Integer(
        string="Pending product(s)", compute="_compute_reviewed_count"
    )

    @api.depends("review_ids", "review_ids.reviewed")
    def _compute_reviewed_count(self):
        for rec in self:
            rec.reviewed_count = len(rec.review_ids.filtered(lambda x: x.reviewed))
            rec.pending_count = len(rec.review_ids.filtered(lambda x: not x.reviewed))

    completed_percent = fields.Float(
        string="% Completed",
        compute="_compute_completed_percent",
    )

    def _compute_completed_percent(self):
        for rec in self:
            product_count = len(rec.review_ids)
            if product_count != 0:
                rec.completed_percent = rec.reviewed_count / product_count * 100
            else:
                rec.completed_percent = False

    days = fields.Integer(
        help="Days from the begining",
        readonly=True,
        compute="_compute_revision_stats",
    )
    velocity = fields.Float(
        string="Velocity (rev/day)",
        help="Revision velocity (revisions/day)",
        readonly=True,
        compute="_compute_revision_stats",
    )
    estimated_total_days = fields.Integer(
        string="Total days (est.)",
        help="Total estimated days of completion at current velocity",
        readonly=True,
        compute="_compute_revision_stats",
    )
    estimated_date = fields.Date(
        string="Date (est.)",
        help="Estimated date of completion at current velocity (excluding weekends)",
        readonly=True,
        compute="_compute_revision_stats",
    )
    estimated_remaining_days = fields.Integer(
        string="Remaining days (est.)",
        help="Remaining days at current velocity (excluding weekends)",
        readonly=True,
        compute="_compute_revision_stats",
    )
    estimated_days_late = fields.Integer(
        string="Days late (est.)",
        help="Days late at current velocity (excluding weekends)",
        readonly=True,
        compute="_compute_revision_stats",
    )

    def _compute_revision_stats(self):
        today = fields.date.today()
        from_string = fields.Date.from_string
        for rec in self:
            total_count = len(rec.review_ids)

            rec.days = (today - from_string(rec.start_date)).days

            days_from = rec.days
            if days_from != 0:
                rec.velocity = rec.reviewed_count / days_from

            if rec.velocity:
                rec.estimated_total_days = total_count / rec.velocity

                work_days = 0
                est_date = from_string(rec.start_date)
                while work_days < rec.estimated_total_days:
                    if est_date.isoweekday() not in (6, 7):
                        work_days += 1
                    est_date += datetime.timedelta(days=1)

                rec.estimated_date = est_date - datetime.timedelta(days=1)

                remaining_days = 0
                cur_date = today
                while cur_date <= from_string(rec.estimated_date):
                    if cur_date.isoweekday() not in (6, 7):
                        remaining_days += 1
                    cur_date += datetime.timedelta(days=1)

                rec.estimated_remaining_days = remaining_days

                if rec.due_date:
                    days_late = 0
                    date0 = from_string(rec.due_date)
                    date1 = from_string(rec.estimated_date)
                    sign = 1
                    if date0 > date1:
                        date0, date1 = date1, date0
                        sign = -1

                    while date0 <= date1:
                        if date0.isoweekday() not in (6, 7):
                            days_late += 1
                        date0 += datetime.timedelta(days=1)

                    rec.estimated_days_late = days_late * sign
            else:
                rec.estimated_date = False
                rec.estimated_days_late = False
                rec.estimated_total_days = False
                rec.estimated_remaining_days = False

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The review package name must be unique!"),
    ]

    def action_products(self):
        return {
            "name": _("Pack products"),
            "type": "ir.actions.act_window",
            "res_model": "lighting.product",
            "views": [(False, "kanban"), (False, "tree"), (False, "form")],
            "domain": [("id", "in", self.review_ids.mapped("product_id.id"))],
            "context": {"default_review_ids": [(0, False, {"package_id": self.id})]},
        }

    def action_product_reviewed(self):
        return {
            "name": _("Reviewed products"),
            "type": "ir.actions.act_window",
            "res_model": "lighting.product",
            "views": [(False, "kanban"), (False, "tree"), (False, "form")],
            "domain": [
                (
                    "id",
                    "in",
                    self.review_ids.filtered(lambda x: x.reviewed).mapped(
                        "product_id.id"
                    ),
                )
            ],
            "context": {
                "default_review_ids": [
                    (0, False, {"package_id": self.id, "reviewed": True})
                ]
            },
        }

    def action_product_pending(self):
        return {
            "name": _("Pending products"),
            "type": "ir.actions.act_window",
            "res_model": "lighting.product",
            "views": [(False, "kanban"), (False, "tree"), (False, "form")],
            "domain": [
                (
                    "id",
                    "in",
                    self.review_ids.filtered(lambda x: not x.reviewed).mapped(
                        "product_id.id"
                    ),
                )
            ],
            "context": {
                "default_review_ids": [
                    (0, False, {"package_id": self.id, "reviewed": False})
                ]
            },
        }

    def copy(self, default=None):
        self.ensure_one()
        default = dict(
            default or {},
            name=_("%s (copy)") % self.name,
        )

        return super().copy(default)
