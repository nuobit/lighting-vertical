# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions 2025 - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProjectType(models.Model):
    _name = "lighting.project.type"
    _description = "Lighting Project Type"
    _order = "name"

    name = fields.Char(
        required=True,
    )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The keyword must be unique!"),
    ]
