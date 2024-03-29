# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import ftplib
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class FTPAttachmentBackend(models.Model):
    _name = "ftp.attachment.backend"
    _inherit = "connector.backend"

    _description = "FTP attachment Configuration"

    @api.model
    def _select_state(self):
        return [
            ("draft", "Draft"),
            ("checked", "Checked"),
            ("production", "In Production"),
        ]

    name = fields.Char(
        required=True,
    )
    sequence = fields.Integer(
        required=True,
        default=1,
    )
    host = fields.Char(
        required=True,
    )
    port = fields.Integer(
        required=True,
        default=21,
    )
    username = fields.Char(
        required=True,
    )
    password = fields.Char(
        required=True,
    )
    output = fields.Text(
        readonly=True,
    )
    active = fields.Boolean(
        default=True,
    )
    state = fields.Selection(
        selection="_select_state",
        default="draft",
    )

    def button_reset_to_draft(self):
        self.ensure_one()
        self.write({"state": "draft", "output": None})

    def get_ftp_connection(self, timeout=None):
        ftp = ftplib.FTP()  # pylint: disable=E8106
        ftp.encoding = "utf-8"
        connect_params = {"host": self.host, "port": self.port}
        if timeout:
            connect_params["timeout"] = timeout
        ftp.connect(**connect_params)
        ftp.login(user=self.username, passwd=self.password)
        return ftp

    def _check_connection(self):
        self.ensure_one()
        try:
            ftp = self.get_ftp_connection(timeout=10)
            ftp.quit()
        except Exception as e:
            raise ValidationError(_("Error connecting to ftp: %s") % str(e)) from e
        else:
            self.output = "OK"

    def button_check_connection(self):
        self._check_connection()
        self.write({"state": "checked"})

    def upload_packages(self):
        packages = self.env["lighting.attachment.package"].search([("auto", "=", True)])
        for pkg in packages.sorted(lambda x: (x.type_id.sequence, x.id)):
            pkg.with_delay().upload(self, generate=True)

    @api.model
    def get_default(self):
        backend = self.env["ftp.attachment.backend"].search(
            [("state", "=", "checked")], order="sequence,id desc", limit=1
        )
        if not backend:
            raise ValidationError(_("No checked FTP configuration found"))
        return backend

    @api.model
    def _scheduler_upload_packages(self):
        backend = self.get_default()
        backend.upload_packages()
