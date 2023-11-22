# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductAuxiliaryEquipmentBrand(models.Model):
    _name = "lighting.product.auxiliaryequipmentbrand"
    _order = "name"

    name = fields.Char(
        string="Auxiliary equipment brand", required=True, translate=False
    )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The auxiliary equipment brand must be unique!"),
    ]
