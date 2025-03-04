# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError


class LightingImportAttachment(models.Model):
    _inherit = "lighting.import.attachment"

    @api.model
    def get_valid_attach_types(self):
        self.ensure_one()
        return self.env["lighting.attachment.type"].search([]).mapped("code")

    def action_check(self):
        valid_attach_types = self.get_valid_attach_types()
        for rec in self:
            if not rec.file_ids:
                raise ValidationError(_("No attachments to check"))
            rec.file_ids.check(valid_attach_types)
            if not rec.file_ids.filtered(lambda r: r.message_info != "checked"):
                rec.state = "checked"

    def action_import(self):
        valid_attach_types = self.get_valid_attach_types()
        for rec in self:
            if rec.file_ids.filtered(lambda r: r.message_info != "checked"):
                raise ValidationError(
                    _("All attachments must be checked before importing")
                )
            rec.file_ids.import_attachments(valid_attach_types)
