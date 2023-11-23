# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingLanguage(models.Model):
    _name = "lighting.language"
    _description = "Language"
    _order = "code"

    code = fields.Char(
        required=True,
    )
    name = fields.Char(
        string="Language",
        required=True,
        translate=True,
    )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The language must be unique!"),
        ("code_uniq", "unique (code)", "The language code must be unique!"),
    ]
