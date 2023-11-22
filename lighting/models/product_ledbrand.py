# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductLedBrand(models.Model):
    _name = "lighting.product.ledbrand"
    _order = "name"

    name = fields.Char(string="LED brand", required=True)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The LED brand must be unique!"),
    ]
