# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

from .tools import check_record_code_format


class LightingProductFinishType(models.Model):
    _name = "lighting.product.finish.type"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Product Finish Type"
    _order = "name"

    name = fields.Char(
        required=True,
        translate=True,
        tracking=True,
    )

    code = fields.Char(
        required=True,
        tracking=True,
    )

    family_ids = fields.Many2many(
        comodel_name="lighting.product.family",
        compute="_compute_family_ids",
        readonly=True,
        string="Families",
    )

    def _compute_family_ids(self):
        Family = self.env["lighting.product.family"]
        finish_type_fields = Family.get_finish_type_fields()
        for rec in self:
            domain = []
            for field in finish_type_fields:
                domain = expression.OR([domain, [(field.name, "in", rec.ids)]])
            rec.family_ids = Family.search(domain)

    family_count = fields.Integer(
        compute="_compute_family_count",
    )

    def _compute_family_count(self):
        for record in self:
            record.family_count = len(record.family_ids)

    product_count = fields.Integer(
        compute="_compute_product_count",
    )

    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec.family_ids.product_ids)

    @api.constrains("code")
    def _check_code_format(self):
        for rec in self:
            check_record_code_format(rec.code)

    @api.constrains("code")
    def _check_code_used(self):
        for rec in self:
            if rec.family_ids:
                raise ValidationError(
                    _(
                        "The code cannot be changed because it is used in the families %s"
                    )
                    % rec.family_ids.mapped("name")
                )

    def action_finish_type_families(self):
        self.ensure_one()
        # get the base action
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "lighting.lighting_product_finish_type_action_family"
        )
        # build the domain
        domain = action["domain"] or []
        domain = expression.AND(
            [
                domain,
                [("id", "in", self.family_ids.ids)],
            ]
        )
        if domain:
            action["domain"] = domain
        # build the context
        finish_type_fields = self.env[
            "lighting.product.family"
        ].get_finish_type_fields()
        context = safe_eval(action["context"])
        for field in finish_type_fields:
            context["default_%s" % field.name] = self.id
        if context:
            action["context"] = context
        return action

    def action_finish_type_products(self):
        self.ensure_one()
        # get the base action
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "lighting.lighting_product_finish_type_action_product"
        )
        # build the domain
        domain = action["domain"] or []
        domain = expression.AND(
            [
                domain,
                [("id", "in", self.family_ids.product_ids.ids)],
            ]
        )
        if domain:
            action["domain"] = domain
        return action

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The finish type name must be unique!"),
        ("code_uniq", "unique (code)", "The finish type code must be unique!"),
    ]
