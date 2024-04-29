# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models


class LightingImportAttachment(models.Model):
    _inherit = "lighting.import.attachment"

    def _states_attachments(self):
        return [
            ("draft", _("Draft")),
            ("checked", _("Checked")),
            ("pending", _("Pending")),
            ("imported", _("Imported")),
        ]

    @api.model
    def change_state_workflow(self):
        state = super().change_state_workflow()
        state.update(
            {
                "checked": state["checked"] + ["pending"],
                "pending": ["imported"],
            }
        )
        return state

    queue_job_import = fields.Boolean(default=False)
    error_file_ids = fields.One2many(
        comodel_name="lighting.import.attachment.file",
        inverse_name="import_attachment_id",
        domain=[
            "|",
            ("message_info", "not in", (False, "checked", "imported")),
            ("job_state", "not in", (False, "done")),
        ],
    )

    @api.depends("file_ids", "file_ids.message_info")
    def _compute_state(self):
        for rec in self:
            new_env = api.Environment(self.env.cr, self.env.uid, self.env.context)
            rec = new_env[self._name].browse(rec.id)
            if rec.queue_job_import:
                job_states = {file.job_state for file in rec.file_ids}
                if rec.state == "checked" and {"pending", "error"} & job_states:
                    rec.state = "pending"
        return super()._compute_state()
