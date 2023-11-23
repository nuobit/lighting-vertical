# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class LightingProductApplication(models.Model):
    _name = "lighting.product.application"
    _description = "Product Application"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence"

    name = fields.Char(
        string="Application",
        required=True,
        translate=True,
    )
    sequence = fields.Integer(
        required=True,
        default=1,
        help="The sequence field is used to define order",
    )

    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
    )

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env["lighting.product"].search_count(
                [("application_ids", "=", record.id)]
            )

    attachment_ids = fields.One2many(
        comodel_name="lighting.product.application.attachment",
        inverse_name="application_id",
        string="Attachments",
        copy=True,
        tracking=True,
    )
    attachment_count = fields.Integer(
        compute="_compute_attachment_count",
        string="Attachment(s)",
    )

    @api.depends("attachment_ids")
    def _compute_attachment_count(self):
        for rec in self:
            rec.attachment_count = len(rec.attachment_ids)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The application must be unique!"),
    ]

    def unlink(self):
        records = self.env["lighting.product"].search(
            [("application_ids", "in", self.ids)]
        )
        if records:
            raise UserError(
                _("You are trying to delete a record that is still referenced!")
            )
        return super(LightingProductApplication, self).unlink()
