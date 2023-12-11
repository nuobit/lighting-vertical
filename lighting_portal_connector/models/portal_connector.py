# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingPortalConnectorSettings(models.Model):
    _name = "lighting.portal.connector.settings"
    _description = "Lighting Portal Connector Settings"
    _order = "sequence"

    sequence = fields.Integer(
        required=True,
        default=1,
        help="The sequence field is used to define the priority of settngs",
    )
    host = fields.Char(
        required=True,
    )
    port = fields.Integer(
        required=True,
    )
    schema = fields.Char(
        required=True,
    )
    username = fields.Char(
        required=True,
    )
    password = fields.Char(
        required=True,
    )

    _sql_constraints = [
        (
            "settings_uniq",
            "unique (host, port, username)",
            "The host, port, username must be unique!",
        ),
    ]

    def name_get(self):
        vals = []
        for rec in self:
            name = "%s@%s:%i" % (
                rec.username,
                rec.host,
                rec.port,
            )
            vals.append((rec.id, name))
        return vals
