# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingExportTemplateAttachmentUrl(models.Model):
    _name = "lighting.export.template.attachment.url"
    _order = "sequence,id"

    sequence = fields.Integer(
        required=True,
        default=1,
        help="The sequence field is used to define order",
    )
    type_id = fields.Many2one(
        comodel_name="lighting.attachment.type",
        ondelete="cascade",
        required=True,
    )
    max_count = fields.Integer(
        string="Max. count",
        default=-1,
    )
    template_id = fields.Many2one(
        comodel_name="lighting.export.template",
        ondelete="cascade",
        required=True,
    )

    _sql_constraints = [
        (
            "line_uniq",
            "unique (type_id,template_id)",
            "The template attachment Url must be unique per template!",
        ),
    ]
