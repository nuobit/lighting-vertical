# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingCatalog(models.Model):
    _inherit = "lighting.catalog"

    project_ids = fields.Many2many(
        compute="_compute_project_ids",
        comodel_name="lighting.project",
        string="Projects",
        readonly=True,
    )

    def _compute_project_ids(self):
        for record in self:
            family_ids = (
                self.env["lighting.product"]
                .search([("catalog_ids", "in", record.id)])
                .mapped("family_ids")
            )
            record.project_ids = self.env["lighting.project"].search(
                [("family_ids", "in", family_ids.mapped("id"))]
            )

    project_count = fields.Integer(
        compute="_compute_project_count",
        string="Projects(s)",
    )

    def _compute_project_count(self):
        for rec in self:
            rec.project_count = len(rec.project_ids)

    def get_catalog_projects(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "lighting_project.product_catalog_action_project"
        )
        action.update({"domain": [("id", "in", self.project_ids.mapped("id"))]})
        return action
