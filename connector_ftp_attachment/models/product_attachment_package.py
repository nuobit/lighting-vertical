# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.queue_job.job import job

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class LightingAttachmentPackage(models.Model):
    _inherit = 'lighting.attachment.package'

    auto = fields.Boolean(
        string="Auto",
        default=True,
    )

    last_upload = fields.Datetime(
        string="Last upload",
        readonly=True,
    )

    @job(default_channel='root.ftpattach')
    def upload(self, backend, generate=False):
        self.ensure_one()
        if generate:
            self.generate_file_button()
        ftp = backend.get_ftp_connection()
        full_path = self.env['ir.attachment']._full_path(self.attachment_id.store_fname)
        self.last_upload = fields.datetime.now()
        with open(full_path, 'rb') as f:
            ftp.storbinary('STOR %s' % self.datas_fname, f)
        ftp.quit()

    def upload_button(self):
        backend = self.env['ftp.attachment.backend'].get_default()
        self.upload(backend)
