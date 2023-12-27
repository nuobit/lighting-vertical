# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingExportTemplateField(models.Model):
    _name = "lighting.export.template.field"
    _order = "sequence"

    sequence = fields.Integer(
        required=True,
        default=1,
        help="The sequence field is used to define order",
    )
    sequence_aux = fields.Integer(
        related="sequence",
        string="Sequence",
    )
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        ondelete="cascade",
        domain=[("model", "=", "lighting.product")],
        required=True,
    )
    field_name = fields.Char(
        related="field_id.name",
        readonly=True,
    )
    field_ttype = fields.Selection(
        related="field_id.ttype",
        readonly=True,
    )
    subfield_name = fields.Char(
        string="Subfield",
    )
    multivalue_method = fields.Selection(
        selection=[("by_field", "By Field"), ("by_separator", "By Separator")],
    )
    multivalue_key = fields.Char()
    multivalue_separator = fields.Char()
    multivalue_order = fields.Boolean(
        help="Order the subelements by sequence",
        default=True,
    )
    effective_field_name = fields.Char()
    conv_code = fields.Char(
        string="Conversion Code",
    )
    translate = fields.Boolean()
    label = fields.Char(
        translate=True,
    )
    template_id = fields.Many2one(
        comodel_name="lighting.export.template",
        ondelete="cascade",
        required=True,
    )

    _sql_constraints = [
        (
            "line_uniq",
            "unique (field_id,template_id)",
            "The template field must be unique per template!",
        ),
    ]
