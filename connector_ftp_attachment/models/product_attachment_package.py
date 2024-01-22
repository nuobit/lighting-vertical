# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingAttachmentPackage(models.Model):
    _inherit = "lighting.attachment.package"

    auto = fields.Boolean(
        default=True,
    )
    last_upload = fields.Datetime(
        readonly=True,
    )

    # TODO: Create channel
    # @job(default_channel="root.ftpattach")
    def upload(self, backend, generate=False):
        self.ensure_one()
        if generate:
            self.generate_file_button()
        ftp = backend.get_ftp_connection()
        full_path = self.env["ir.attachment"]._full_path(self.attachment_id.store_fname)
        self.last_upload = fields.datetime.now()
        with open(full_path, "rb") as f:
            ftp.storbinary("STOR %s" % self.datas_fname, f)
        ftp.quit()

    def upload_button(self):
        backend = self.env["ftp.attachment.backend"].get_default()
        self.upload(backend)
