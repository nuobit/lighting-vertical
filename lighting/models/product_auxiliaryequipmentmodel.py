# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductAuxiliaryEquipmentModel(models.Model):
    _name = "lighting.product.auxiliaryequipmentmodel"
    _rec_name = "reference"
    _order = "product_id,date desc"

    reference = fields.Char(string="Reference")
    brand_id = fields.Many2one(
        comodel_name="lighting.product.auxiliaryequipmentbrand",
        ondelete="restrict",
        string="Brand",
        required=True,
    )
    date = fields.Date(string="Date", required=True)

    product_id = fields.Many2one(
        comodel_name="lighting.product", ondelete="cascade", string="Product"
    )

    _sql_constraints = [
        ("prodate_uniq", "unique (product_id, date)", "The date must be unique!"),
    ]
