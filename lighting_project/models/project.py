# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, fields, models

YEAR_RANGE = 100


class LightingProject(models.Model):
    _name = "lighting.project"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"
    _description = "Project"

    name = fields.Char(
        required=True,
        tracking=True,
    )
    city = fields.Char(
        required=True,
        tracking=True,
    )
    country_id = fields.Many2one(
        comodel_name="res.country",
        ondelete="restrict",
        required=True,
    )
    type_ids = fields.Many2many(
        comodel_name="lighting.project.type",
        string="Types",
        relation="lighting_project_product_type_rel",
        column1="project_id",
        column2="type_id",
        required=True,
        tracking=True,
    )
    prescriptor = fields.Char(
        tracking=True,
    )
    year = fields.Integer(
        default=fields.datetime.now().year,
        tracking=True,
    )
    family_ids = fields.Many2many(
        comodel_name="lighting.product.family",
        string="Families",
        relation="lighting_project_product_family_rel",
        column1="project_id",
        column2="family_id",
        required=True,
        tracking=True,
    )
    description = fields.Text(
        translate=True,
        tracking=True,
    )
    agent_id = fields.Many2one(
        comodel_name="lighting.project.agent",
        required=True,
        tracking=True,
    )
    auth_contact_name = fields.Char(
        string="Name",
        tracking=True,
    )
    auth_contact_email = fields.Char(
        string="e-mail",
        tracking=True,
    )
    auth_contact_phone = fields.Char(
        string="Phone",
        tracking=True,
    )
    attachment_ids = fields.One2many(
        comodel_name="lighting.project.attachment",
        inverse_name="project_id",
        string="Attachments",
        copy=True,
        tracking=True,
    )
    attachment_count = fields.Integer(
        compute="_compute_attachment_count",
        string="Attachment(s)",
    )

    @api.depends("attachment_ids")
    def _compute_attachment_count(self):
        for rec in self:
            rec.attachment_count = len(rec.attachment_ids)

    catalog_ids = fields.Many2many(
        compute="_compute_catalog_ids",
        comodel_name="lighting.catalog",
        string="Catalogs",
        readonly=True,
        tracking=True,
    )

    @api.depends("family_ids")
    def _compute_catalog_ids(self):
        for rec in self:
            rec.catalog_ids = (
                self.env["lighting.product"]
                .search([("family_ids", "in", rec.family_ids.mapped("id"))])
                .mapped("catalog_ids")
            )

    def print_project_sheet(self):
        return self.env.ref(
            "lighting_project.project_sheet_report_action"
        ).report_action(self)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The keyword must be unique!"),
    ]

    @api.constrains("year")
    def _check_year(self):
        current_year = fields.datetime.now().year
        min_year = current_year - YEAR_RANGE
        max_year = current_year + YEAR_RANGE
        for rec in self:
            if rec.year < min_year or rec.year > max_year:
                raise models.ValidationError(
                    _("Year must be between %(min_year)s and %(max_year)s")
                    % {
                        "min_year": min_year,
                        "max_year": max_year,
                    }
                )
