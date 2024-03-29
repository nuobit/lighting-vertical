# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProjectAgent(models.Model):
    _name = "lighting.project.agent"
    _order = "name"

    name = fields.Char(
        required=True,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        ondelete="restrict",
        string="Odoo user",
        required=False,
    )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The keyword must be unique!"),
    ]
