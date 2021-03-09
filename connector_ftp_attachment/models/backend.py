# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import ftplib

_logger = logging.getLogger(__name__)


class FTPAttachmentBackend(models.Model):
    _name = 'ftp.attachment.backend'
    _inherit = 'connector.backend'

    _description = 'FTP attachment Configuration'

    @api.model
    def _select_state(self):
        return [('draft', 'Draft'),
                ('checked', 'Checked'),
                ('production', 'In Production')]

    name = fields.Char('Name', required=True)

    sequence = fields.Integer('Sequence', required=True, default=1)

    host = fields.Char('Host', required=True)
    port = fields.Integer('Port', required=True, default=21)
    username = fields.Char('Username', required=True)
    password = fields.Char('Password', required=True)

    output = fields.Text('Output', readonly=True)

    active = fields.Boolean(
        string='Active',
        default=True
    )
    state = fields.Selection(
        selection='_select_state',
        string='State',
        default='draft'
    )

    @api.multi
    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({'state': 'draft', 'output': None})

    def get_ftp_connection(self, timeout=None):
        ftp = ftplib.FTP()
        ftp.encoding = 'utf-8'
        connect_params = {
            'host': self.host,
            'port': self.port
        }
        if timeout:
            connect_params['timeout'] = timeout
        ftp.connect(**connect_params)
        ftp.login(
            user=self.username,
            passwd=self.password)
        return ftp

    @api.multi
    def _check_connection(self):
        self.ensure_one()
        try:
            ftp = self.get_ftp_connection(timeout=10)
            ftp.quit()
        except Exception as e:
            raise UserError(_("Error connecting to ftp: %s") % str(e))
        else:
            self.output = "OK"

    @api.multi
    def button_check_connection(self):
        self._check_connection()
        self.write({'state': 'checked'})

    def upload_packages(self):
        packages = self.env['lighting.attachment.package'].search([
            ('auto', '=', True)
        ])
        for pkg in packages:
            pkg.with_delay().upload(self, generate=True)
        return True
