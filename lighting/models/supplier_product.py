# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductSupplier(models.Model):
    _name = "lighting.product.supplier"
    _description = "Product Supplier"
    _rec_name = "supplier_id"
    _order = "sequence"

    sequence = fields.Integer(
        required=True,
        default=1,
        help="The sequence field is used to define the priority of suppliers",
    )
    supplier_id = fields.Many2one(
        comodel_name="lighting.supplier",
        ondelete="restrict",
        string="Supplier",
        required=True,
    )
    reference = fields.Char()
    product_id = fields.Many2one(
        comodel_name="lighting.product",
        ondelete="cascade",
    )
