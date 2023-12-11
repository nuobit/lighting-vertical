# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class LightingProductFamily(models.Model):
    _inherit = "lighting.product.family"

    project_count = fields.Integer(
        compute="_compute_project_count",
        string="Projects(s)",
    )

    def _compute_project_count(self):
        for rec in self:
            rec.project_count = self.env["lighting.project"].search_count(
                [("family_ids", "=", rec.id)]
            )

    @api.ondelete(at_uninstall=False)
    def _unlink_except_linked_project(self):
        for rec in self:
            if rec.project_count:
                raise UserError(
                    _("You are trying to delete a record that is still referenced!")
                )
