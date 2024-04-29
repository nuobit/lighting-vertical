# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models


class LightingImportAttachmentFile(models.Model):
    _inherit = "lighting.import.attachment.file"

    file_jobs_ids = fields.Many2many(
        comodel_name="queue.job",
        relation="lighting_import_attachment_file_queue_job_rel",
        column1="file_id",
        column2="job_id",
        string="Queue Jobs",
        copy=False,
    )
    job_state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("done", "Done"),
            ("error", "Error"),
            ("cancel", "Cancelled"),
        ],
        compute="_compute_job_state",
        default=False,
        store=True,
    )

    @api.depends("file_jobs_ids", "file_jobs_ids.state")
    def _compute_job_state(self):
        for rec in self:
            if rec.file_jobs_ids:
                states = set(rec.file_jobs_ids.mapped("state"))
                if {"enqueued", "pending", "started", "wait_dependencies"} & states:
                    rec.job_state = "pending"
                elif {"done"} & states:
                    rec.job_state = "done"
                elif {"cancelled"} == states:
                    rec.job_state = "cancel"
                else:
                    rec.job_state = "error"
            else:
                rec.job_state = False

    def import_attachments(self):
        if not self.import_attachment_id.queue_job_import:
            return super().import_attachments()
        queue_obj = self.env["queue.job"]
        for rec in self:
            new_delay = rec.with_delay().execute_delayed_import_attachments()
            job = queue_obj.search([("uuid", "=", new_delay.uuid)], limit=1)
            rec.file_jobs_ids |= job
        self.import_attachment_id._compute_state()

    def execute_delayed_import_attachments(self):
        self.ensure_one()
        return super().import_attachments()

    def action_show_queue_job_details(self):
        self.ensure_one()
        view = self.env.ref(
            "lighting_import_attachment_product_queue_job."
            "lighting_import_attachment_file_queue_job_view_form"
        )
        return {
            "name": _("Queue Job Details"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "lighting.import.attachment.file",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": self.id,
            "context": dict(
                self.env.context,
            ),
        }
