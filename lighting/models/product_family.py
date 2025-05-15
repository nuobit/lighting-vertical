# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class LightingProductFamily(models.Model):
    _name = "lighting.product.family"
    _description = "Product Family"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence"

    name = fields.Char(
        string="Family",
        required=True,
    )
    # TODO: restrict len(code)=4
    code = fields.Char(
        required=False,
    )
    is_export = fields.Boolean()
    description = fields.Text(
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
                [("family_ids", "=", record.id)]
            )

    discontinued_product_percent = fields.Float(
        compute="_compute_discontinued_product_percent",
        string="% Discontinued product(s)",
    )

    def _compute_discontinued_product_percent(self):
        for record in self:
            percent = 0
            if record.product_count != 0:
                discontinued_product_count = self.env["lighting.product"].search_count(
                    [("family_ids", "=", record.id), ("state_marketing", "=", "D")]
                )
                percent = discontinued_product_count / record.product_count * 100
            record.discontinued_product_percent = percent

    attachment_ids = fields.One2many(
        comodel_name="lighting.product.family.attachment",
        inverse_name="family_id",
        string="Attachments",
        copy=True,
        tracking=True,
    )
    attachment_count = fields.Integer(
        string="Attachment(s)",
        compute="_compute_attachment_count",
    )

    @api.depends("attachment_ids")
    def _compute_attachment_count(self):
        for rec in self:
            rec.attachment_count = len(rec.attachment_ids)

    finish_type_id = fields.Many2one(
        comodel_name="lighting.product.finish.type",
        string="Finish Type",
        ondelete="restrict",
        tracking=True,
    )

    finish2_type_id = fields.Many2one(
        comodel_name="lighting.product.finish.type",
        string="Finish2 Type",
        ondelete="restrict",
        tracking=True,
    )

    def get_finish_type(self, finish_field_name):
        if self:
            finish_types = {x[finish_field_name] for x in self}
            if len(finish_types) != 1:
                raise ValidationError(
                    _(
                        "The field '%(finish_field_string)s' is not consistent across "
                        "all families '%(families)s'!"
                    )
                    % {
                        "finish_field_string": self._fields[finish_field_name].string,
                        "families": ", ".join([x.name for x in self]),
                    }
                )
            return list(finish_types)[0]
        return False

    @api.model
    def get_finish_type_fields(self):
        """Get the finish type fields for the product family."""
        return [
            f for k, f in self._fields.items() if re.match(r"^finish[0-9]*_type_id$", k)
        ]

    def check_finish_type_consistency(self):
        """Check the finish type consistency between all familes of the recordset"""
        for field in self.get_finish_type_fields():
            self.get_finish_type(field.name)

    @api.constrains("finish_type_id", "finish2_type_id")
    def _check_product_finish_type_consistency(self):
        for rec in self:
            products = self.env["lighting.product"].search(
                [("family_ids", "in", rec.ids)]
            )
            products.family_ids.check_finish_type_consistency()

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The family must be unique!"),
    ]

    def unlink(self):
        records = self.env["lighting.product"].search([("family_ids", "in", self.ids)])
        if records:
            raise UserError(
                _("You are trying to delete a record that is still referenced!")
            )
        return super(LightingProductFamily, self).unlink()
