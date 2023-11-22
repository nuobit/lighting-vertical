# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingSupplier(models.Model):
    _name = "lighting.supplier"
    _order = "name"

    name = fields.Char(string="Description", required=True)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The supplier description must be unique!"),
    ]
