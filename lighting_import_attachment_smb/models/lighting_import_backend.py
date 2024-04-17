# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from smb.SMBConnection import SMBConnection

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class LightingImportBackend(models.Model):
    _name = "lighting.import.backend"
    _description = "Lighting Import Backend"

    name = fields.Char(required=True)
    host = fields.Char(help="Host address of the SMB server", required=True)
    user = fields.Char(help="User to connect to the SMB server", required=True)
    password = fields.Char(required=True)
    port = fields.Integer(default=445, required=True)
    domain = fields.Char()
    netbios_remote_server = fields.Char(string="NetBIOS Remote Server", required=True)
    shared_resource = fields.Char(required=True)
    folder = fields.Char(required=True, default="/")
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("validated", "Validated"),
        ],
        default="draft",
        required=True,
    )

    def smb_connect(self):
        conn = SMBConnection(
            self.user,
            self.password,
            "",
            self.netbios_remote_server,
            domain=self.domain or "",
            use_ntlm_v2=True,
            is_direct_tcp=True,
        )
        ok = conn.connect(self.host, self.port)
        if not ok:
            raise ValidationError(
                _("Cannot connect to Host %(host)s on port %(port)i")
                % {"host": self.host, "port": self.port}
            )
        return conn

    def button_check_connection(self):
        self.ensure_one()
        try:
            conn = self.smb_connect()
            conn.listPath(self.shared_resource, self.folder)
            conn.close()
        except Exception as exc:
            raise ValidationError(
                _(
                    "Failed to connect or read from the SMB server. "
                    "Wrong Connection Parameters:\n%s"
                )
                % exc
            ) from exc
        self.state = "validated"

    def button_reset_to_draft(self):
        self.ensure_one()
        self.state = "draft"
