# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import requests

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class SapB1Backend(models.Model):
    _name = 'sapb1.backend'
    _inherit = 'connector.backend'

    _description = 'SAP B1 Backend Configuration'
    _order = 'sequence'

    @api.model
    def _select_state(self):
        return [('draft', 'Draft'),
                ('checked', 'Checked'),
                ('production', 'In Production')]

    name = fields.Char('Name', required=True)

    sequence = fields.Integer('Sequence', required=True, default=1)

    company_id = fields.Many2one(
        comodel_name='res.company',
        index=True,
        required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'sapb1.backend'),
        string='Company',
    )

    # fileserver
    fileserver_host = fields.Char('Hostname', required=True)
    fileserver_port = fields.Integer('Port', default=22, required=True)

    fileserver_username = fields.Char('Username', required=True)
    fileserver_password = fields.Char('Password', required=True)

    fileserver_basepath = fields.Char('Base path', required=True)

    fileserver_version = fields.Text('Version', readonly=True)

    # database
    db_host = fields.Char('Hostname', required=True)
    db_port = fields.Integer('Port', default=30015, required=True)

    db_schema = fields.Char('Schema', required=True)

    db_username = fields.Char('Username', required=True)
    db_password = fields.Char('Password', required=True)

    db_version = fields.Text('Version', readonly=True)

    # servicelayer
    sl_port = fields.Integer('Port', default=50000, required=True)

    sl_ssl_enabled = fields.Boolean('SSL enabled', default=True)
    sl_base_url = fields.Char('Base URL', default='/b1s/v1', required=True)

    sl_url = fields.Char(
        string='URL',
        store=True,
        compute="_compute_sl_url",
    )

    sl_username = fields.Char('Username', required=True)
    sl_password = fields.Char('Password', required=True)

    @api.depends('sl_ssl_enabled', 'db_host', 'sl_port', 'sl_base_url')
    def _compute_sl_url(self):
        for rec in self:
            rec.sl_url = requests.compat.urlunparse([
                'http%s' % (rec.sl_ssl_enabled and 's' or '',),
                '%s:%i' % (rec.db_host, rec.sl_port),
                rec.sl_base_url,
                None, None, None,
            ])

    sl_version = fields.Text('Version', readonly=True)

    active = fields.Boolean(
        string='Active',
        default=True
    )
    state = fields.Selection(
        selection='_select_state',
        string='State',
        default='draft'
    )

    state_marketing_map = fields.One2many(
        string="State Marketing Map",
        comodel_name="sapb1.backend.state.marketing.map",
        inverse_name="backend_id",
    )

    catalog_map = fields.One2many(
        string="Catalog Map",
        comodel_name="sapb1.backend.catalog.map",
        inverse_name="backend_id",
    )

    language_map = fields.One2many(
        string="Langauage Map",
        comodel_name="sapb1.backend.lang.map",
        inverse_name="backend_id",
    )

    @api.multi
    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({'state': 'draft', 'version': None})

    @api.multi
    def _check_connection(self):
        self.ensure_one()
        # TODO

    @api.multi
    def button_check_connection(self):
        for rec in self:
            rec._check_connection()
            rec.write({'state': 'checked'})

    # data attributes
    import_products_since_date = fields.Datetime('Import Products since')
    export_products_since_date = fields.Datetime('Export Products since')

    @api.constrains('language_map')
    def _check_sap_main_lang(self):
        for rec in self:
            sap_main_lang = rec.language_map \
                .filtered(lambda x: x.sap_main_lang).mapped('sap_main_lang')
            if len(sap_main_lang) == 0:
                raise ValidationError("You need to select a main language")
            if len(sap_main_lang) > 1:
                raise ValidationError("Only one main language is allowed to select")

    # data methods
    @api.multi
    def import_products_since(self):
        for rec in self:
            since_date = fields.Datetime.from_string(rec.import_products_since_date)
            self.env['sapb1.lighting.product'].with_delay(
            ).import_products_since(
                backend_record=rec)

        return True

    @api.multi
    def export_products_since(self):
        for rec in self:
            since_date = fields.Datetime.from_string(rec.export_products_since_date)
            self.env['sapb1.lighting.product'].with_delay(
            ).export_products_since(
                backend_record=rec)

        return True

    # Scheduler methods
    @api.model
    def get_current_user_company(self):
        if self.env.user.id == self.env.ref('base.user_root').id:
            raise exceptions.ValidationError(_("The cron user cannot be admin"))

        return self.env.user.company_id

    @api.model
    def _scheduler_import_products(self):
        company_id = self.get_current_user_company()
        domain = [
            ('company_id', '=', company_id.id)
        ]
        self.search(domain).import_products_since()
