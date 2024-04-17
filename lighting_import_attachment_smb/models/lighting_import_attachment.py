# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import base64
import tempfile

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class LightingImportAttachment(models.Model):
    _inherit = "lighting.import.attachment"

    source = fields.Many2one(
        comodel_name="lighting.import.backend",
    )

    def button_load_files_from_source(self):
        self.ensure_one()
        if not self.source:
            raise ValidationError(_("Source is not defined."))
        if self.source.state != "validated":
            raise ValidationError(_("Source connection is not validated."))
        conn = self.source.smb_connect()
        files = conn.listPath(self.source.shared_resource, self.source.folder)
        files_ndx = {f.filename: f for f in files if not f.isDirectory}
        for filename, _f in files_ndx.items():
            file_obj = tempfile.NamedTemporaryFile()
            if self.source.folder == "/":
                file_path = "/%s" % filename
            else:
                file_path = "%s/%s" % (self.source.folder.rstrip("/"), filename)
            conn.retrieveFile(self.source.shared_resource, file_path, file_obj)
            file_obj.seek(0)
            file_data = file_obj.read()
            self.file_ids.create(
                {
                    "import_attachment_id": self.id,
                    "datas": base64.b64encode(file_data),
                    "datas_fname": filename,
                }
            )
            file_obj.close()
        conn.close()
