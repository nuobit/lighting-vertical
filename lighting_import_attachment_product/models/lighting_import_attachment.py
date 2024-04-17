# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import ValidationError


class LightingImportAttachment(models.Model):
    _inherit = "lighting.import.attachment"

    def action_check(self):
        for rec in self:
            if not rec.file_ids:
                raise ValidationError(_("No attachments to check"))
            rec.file_ids.check()
            if not rec.file_ids.filtered(lambda r: r.message_info != "checked"):
                rec.state = "checked"

    def action_import(self):
        for rec in self:
            if rec.file_ids.filtered(lambda r: r.message_info != "checked"):
                raise ValidationError(
                    _("All attachments must be checked before importing")
                )
            rec.file_ids.import_attachments()
