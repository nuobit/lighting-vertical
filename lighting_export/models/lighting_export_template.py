# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LightingExportTemplate(models.Model):
    _name = "lighting.export.template"
    _inherit = ["mail.thread", "mail.activity.mixin", "image.mixin"]
    _order = "sequence,name"

    name = fields.Char(
        required=True,
    )
    code = fields.Char(
        required=True,
        copy=False,
    )
    sequence = fields.Integer(
        required=True,
        default=1,
        help="The sequence field is used to define order",
    )
    field_ids = fields.One2many(
        comodel_name="lighting.export.template.field",
        inverse_name="template_id",
        string="Fields",
        copy=True,
    )
    attachment_ids = fields.One2many(
        comodel_name="lighting.export.template.attachment",
        inverse_name="template_id",
        string="File Attachments",
        copy=True,
    )
    max_attachments = fields.Integer(
        string="Max. file attachments",
        default=-1,
    )
    attachment_url_ids = fields.One2many(
        comodel_name="lighting.export.template.attachment.url",
        inverse_name="template_id",
        string="Url Attachments",
        copy=True,
    )
    max_url_attachments = fields.Integer(
        string="Max. Url attachments",
        default=-1,
    )
    lang_ids = fields.Many2many(
        comodel_name="res.lang",
        relation="lighting_export_template_lang_rel",
        column1="template_id",
        column2="lang_id",
        string="Languages",
        domain=[("active", "=", True)],
        tracking=True,
    )
    default_lang_id = fields.Many2one(
        comodel_name="res.lang",
        string="Default Language",
        domain="[('id', 'in', lang_ids)]",
        required=True,
        tracking=True,
    )
    lang_field_format = fields.Selection(
        string="Language Field Format",
        selection=[("postfix", "Postfix")],
        required=True,
        default="postfix",
        help="Only used if multiple languages are selected "
        "and all of them are shown on the same file. "
        "Used to differentiate the same field from "
        "different languages. p.e descrption_EN, description_FR, etc.",
    )

    lang_multiple_files = fields.Boolean(
        help="If enabled multiple files will be generated, one per language",
    )
    hide_empty_fields = fields.Boolean(
        default=True,
    )
    output_type = fields.Selection(
        selection=[],
    )
    domain = fields.Text()

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The template name must be unique!"),
        (
            "code_uniq",
            "unique (code)",
            "The Code should be unique. It identifies the export template",
        ),
    ]

    def add_all_fields(self):
        for rec in self:
            lighting_product_fields_ids = self.env["ir.model.fields"].search(
                [
                    ("model", "=", "lighting.product"),
                    (
                        "name",
                        "in",
                        list(self.env["lighting.product"].fields_get().keys()),
                    ),
                ]
            )
            new_field_ids = lighting_product_fields_ids.filtered(
                lambda x: x.id not in rec.field_ids.mapped("field_id.id")
            ).sorted(lambda x: x.id)

            max_sequence = max(rec.field_ids.mapped("sequence") or [0])
            rec.field_ids = [
                (
                    0,
                    False,
                    {
                        "sequence": max_sequence + i,
                        "field_id": x.id,
                        "translate": x.translate,
                    },
                )
                for i, x in enumerate(new_field_ids, 1)
            ]

    def copy(self, default=None):
        self.ensure_one()
        default = dict(
            default or {},
            name=_("%s (copy)") % self.name,
            image_1920=False,
        )
        return super().copy(default)

    @api.constrains("lang_ids", "default_lang_id")
    def check_languages(self):
        for rec in self:
            if rec.default_lang_id not in rec.lang_ids:
                raise ValidationError(
                    _("Default language should be one of the selected languages")
                )
