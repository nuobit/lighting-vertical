# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models


class LightingImportAttachment(models.Model):
    _name = "lighting.import.attachment"
    _description = "Lighting Import Attachment"
    _order = "date desc"

    def _states_attachments(self):
        return [
            ("draft", _("Draft")),
            ("checked", _("Checked")),
            ("imported", _("Imported")),
        ]

    @api.model
    def change_state_workflow(self):
        return {
            "draft": ["checked"],
            "checked": ["draft", "imported"],
            "imported": None,
        }

    name = fields.Char(required=True)
    date = fields.Date(required=True, default=fields.Date.today)
    state = fields.Selection(
        selection="_states_attachments",
        default="draft",
        compute="_compute_state",
        store=True,
        readonly=False,
        required=True,
    )

    @api.depends("file_ids", "file_ids.message_info")
    def _compute_state(self):
        for rec in self:
            states = {file.message_info for file in rec.file_ids}
            if {"imported"} == states:
                rec.state = "imported"

    file_ids = fields.One2many(
        comodel_name="lighting.import.attachment.file",
        inverse_name="import_attachment_id",
    )
    hide_done = fields.Boolean()
    error_file_ids = fields.One2many(
        comodel_name="lighting.import.attachment.file",
        inverse_name="import_attachment_id",
        domain=[("message_info", "not in", (False, "checked", "imported"))],
    )
    check_error_files = fields.Boolean(compute="_compute_check_error_files")

    def _compute_check_error_files(self):
        for rec in self:
            rec.check_error_files = bool(
                rec.file_ids.filtered(
                    lambda x: x.message_info not in (False, "checked", "imported")
                )
            )

    def action_set_to_draft(self):
        self.state = "draft"

    def action_check(self):
        """Process the files"""
        raise NotImplementedError

    def action_import(self):
        """Import the files"""
        raise NotImplementedError

    def write(self, vals):
        change_state_workflow = self.change_state_workflow()
        for rec in self:
            if "state" in vals:
                if vals["state"] not in change_state_workflow[rec.state]:
                    raise ValueError(
                        _(
                            "It's not allowed to change state "
                            "from %(from_state)s to %(to_state)s"
                        )
                        % {"from_state": rec.state, "to_state": vals["state"]}
                    )
                errors = vals.get("hide_done", rec.hide_done)
                if vals["state"] == "checked" and errors:
                    vals["hide_done"] = False
        return super().write(vals)
