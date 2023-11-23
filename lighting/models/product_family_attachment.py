# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class LightingProductFamilyAttachment(models.Model):
    _name = "lighting.product.family.attachment"
    _description = "Product Family Attachment"
    _order = "sequence"
    _rec_name = "datas_fname"

    name = fields.Text(
        string="Description",
        translate=True,
    )
    sequence = fields.Integer(
        required=True,
        default=1,
        help="The sequence field is used to define order",
    )
    datas = fields.Binary(
        string="Document",
        attachment=True,
        required=True,
    )
    datas_fname = fields.Char(
        string="Filename",
        required=True,
    )
    # TODO:It should be stored?
    attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        compute="_compute_ir_attachment",
    )

    @api.depends("datas")
    def _compute_ir_attachment(self):
        for rec in self:
            attachment_obj = rec.env["ir.attachment"].search(
                [
                    ("res_field", "=", "datas"),
                    ("res_id", "=", rec.id),
                    ("res_model", "=", rec._name),
                ]
            )
            if attachment_obj:
                rec.attachment_id = attachment_obj[0]
            else:
                rec.attachment_id = False

    checksum = fields.Char(
        compute="_compute_checksum",
    )

    @api.depends("attachment_id", "attachment_id.checksum")
    def _compute_checksum(self):
        for rec in self:
            rec.checksum = rec.attachment_id.checksum

    category_id = fields.Many2one(
        comodel_name="lighting.product.category",
        ondelete="cascade",
    )
    is_default = fields.Boolean(
        string="Default",
    )
    family_id = fields.Many2one(
        comodel_name="lighting.product.family",
        ondelete="cascade",
    )
