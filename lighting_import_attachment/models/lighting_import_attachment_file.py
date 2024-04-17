# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LightingImportAttachmentFile(models.Model):
    _name = "lighting.import.attachment.file"
    _description = "Lighting Import Attachment File"
    _order = "message_info"

    import_attachment_id = fields.Many2one(
        comodel_name="lighting.import.attachment",
        required=True,
        ondelete="cascade",
    )
    datas_fname = fields.Char(string="Filename", required=True)
    datas = fields.Binary(string="File", required=True)
    message_info = fields.Selection(
        selection=[
            ("checked", "Checked"),
            ("imported", "Imported"),
        ],
    )
    attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        compute="_compute_ir_attachment",
        readonly=True,
    )

    @api.depends("datas")
    def _compute_ir_attachment(self):
        for rec in self:
            rec.attachment_id = rec.env["ir.attachment"].get_attachment(rec, "datas")

    checksum = fields.Char(
        related="attachment_id.checksum",
    )

    @api.constrains("datas_fname")
    def _check_datas_fname(self):
        for rec in self:
            if rec.import_attachment_id.file_ids.filtered(
                lambda r: r.datas_fname == rec.datas_fname and r.id != rec.id
            ):
                raise ValidationError(_("File %s already exists") % rec.datas_fname)

    @api.constrains("datas")
    def _check_datas(self):
        for rec in self:
            if rec.import_attachment_id.state != "draft":
                raise ValidationError(_("Attachment cannot be uploaded in this state"))
