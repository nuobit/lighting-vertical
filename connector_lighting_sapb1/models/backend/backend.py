# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

import requests

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class LightingSapB1Backend(models.Model):
    _name = "lighting.sapb1.backend"
    _inherit = "connector.extension.backend"
    _description = "Lighting SAP B1 Backend Configuration"
    _order = "sequence"

    name = fields.Char(
        required=True,
    )
    sequence = fields.Integer(
        required=True,
        default=1,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        index=True,
        required=True,
        default=lambda self: self.env["res.company"]._company_default_get(
            "lighting.sapb1.backend"
        ),
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        required=True,
        string="User",
        domain="[('company_id', '=', company_id)]",
    )

    # fileserver
    fileserver_host = fields.Char(
        string="Hostname",
        required=True,
    )
    fileserver_port = fields.Integer(
        string="Port",
        default=22,
        required=True,
    )
    fileserver_username = fields.Char(
        string="Username",
        required=True,
    )
    fileserver_password = fields.Char(
        string="Password",
        required=True,
    )
    fileserver_basepath = fields.Char(
        string="Base path",
        required=True,
    )
    fileserver_version = fields.Text(
        string="Version",
        readonly=True,
    )

    # database
    db_host = fields.Char(
        string="Hostname",
        required=True,
    )
    db_port = fields.Integer(
        string="Port",
        default=30015,
        required=True,
    )
    db_schema = fields.Char(
        string="Schema",
        required=True,
    )
    db_username = fields.Char(
        string="Username",
        required=True,
    )
    db_password = fields.Char(
        string="Password",
        required=True,
    )
    db_version = fields.Text(
        string="Version",
        readonly=True,
    )

    # servicelayer
    sl_port = fields.Integer(
        string="Port",
        default=50000,
        required=True,
    )
    sl_ssl_enabled = fields.Boolean(
        string="SSL enabled",
        default=True,
    )
    sl_base_url = fields.Char(
        string="Base URL",
        default="/b1s/v1",
        required=True,
    )
    sl_url = fields.Char(
        string="URL",
        store=True,
        compute="_compute_sl_url",
    )
    sl_username = fields.Char(
        string="Username",
        required=True,
    )
    sl_password = fields.Char(
        string="Password",
        required=True,
    )

    @api.depends("sl_ssl_enabled", "db_host", "sl_port", "sl_base_url")
    def _compute_sl_url(self):
        for rec in self:
            rec.sl_url = requests.compat.urlunparse(
                [
                    "http%s" % (rec.sl_ssl_enabled and "s" or "",),
                    "%s:%i" % (rec.db_host, rec.sl_port),
                    rec.sl_base_url,
                    None,
                    None,
                    None,
                ]
            )

    sl_version = fields.Text(
        string="Version",
        readonly=True,
    )

    state_marketing_map = fields.One2many(
        comodel_name="lighting.sapb1.backend.state.marketing.map",
        inverse_name="backend_id",
    )
    catalog_map = fields.One2many(
        comodel_name="lighting.sapb1.backend.catalog.map",
        inverse_name="backend_id",
    )
    language_map = fields.One2many(
        comodel_name="lighting.sapb1.backend.lang.map",
        inverse_name="backend_id",
    )

    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({"state": "draft", "version": None})

    def _check_connection(self):
        self.ensure_one()
        # TODO

    def button_check_connection(self):
        for rec in self:
            rec._check_connection()
            rec.write({"state": "validated"})

    import_products_since_date = fields.Datetime(
        string="Import Products since",
    )
    export_products_since_date = fields.Datetime(
        string="Export Products since",
    )

    @api.constrains("language_map")
    def _check_sap_main_lang(self):
        for rec in self:
            sap_main_lang = rec.language_map.filtered(lambda x: x.sap_main_lang).mapped(
                "sap_main_lang"
            )
            if len(sap_main_lang) == 0:
                raise ValidationError(_("You need to select a main language"))
            if len(sap_main_lang) > 1:
                raise ValidationError(_("Only one main language is allowed to select"))

    # data methods
    # TODO: Check changes on import/export
    def import_products_since(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date = fields.Datetime.to_datetime(rec.import_products_since_date)
            rec.import_products_since_date = fields.Datetime.now()
            self.env["lighting.sapb1.product"].import_products_since(
                backend_record=rec, since_date=since_date
            )

    def export_products_since(self):
        self.env.user.company_id = self.company_id
        for rec in self:
            since_date = fields.Datetime.from_string(rec.export_products_since_date)
            rec.export_products_since_date = fields.Datetime.now()
            self.env["lighting.sapb1.product"].export_products_since(
                backend_record=rec, since_date=since_date
            )

    # Scheduler methods
    @api.model
    def get_current_user_company(self):
        if self.env.user.id == self.env.ref("base.user_root").id:
            raise exceptions.ValidationError(_("The cron user cannot be admin"))
        return self.env.user.company_id

    @api.model
    def _scheduler_import_products(self):
        company_id = self.get_current_user_company()
        domain = [("company_id", "=", company_id.id)]
        self.search(domain).import_products_since()

    @api.model
    def _scheduler_export_products(self):
        company_id = self.get_current_user_company()
        domain = [("company_id", "=", company_id.id)]
        self.search(domain).export_products_since()
