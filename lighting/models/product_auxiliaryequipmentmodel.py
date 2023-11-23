# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductAuxiliaryEquipmentModel(models.Model):
    _name = "lighting.product.auxiliaryequipmentmodel"
    _description = "Product Auxiliary Equipment Model"
    _rec_name = "reference"
    _order = "product_id,date desc"

    reference = fields.Char()
    brand_id = fields.Many2one(
        comodel_name="lighting.product.auxiliaryequipmentbrand",
        ondelete="restrict",
        required=True,
    )
    date = fields.Date(
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name="lighting.product",
        ondelete="cascade",
    )

    _sql_constraints = [
        ("prodate_uniq", "unique (product_id, date)", "The date must be unique!"),
    ]
