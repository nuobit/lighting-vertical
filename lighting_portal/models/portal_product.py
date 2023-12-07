# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingPortalProduct(models.Model):
    _name = "lighting.portal.product"
    _description = "Lighting Portal Product"
    _rec_name = "reference"
    _order = "reference"

    reference = fields.Char(
        required=True,
    )
    barcode = fields.Char()
    description = fields.Char()
    catalog = fields.Char()
    qty_available = fields.Integer(
        string="Quantity available",
    )
    product_id = fields.Many2one(
        comodel_name="lighting.product",
        ondelete="set null",
        string="Product",
        groups="lighting_portal.portal_group_manager",
    )

    _sql_constraints = [
        ("reference", "unique (reference)", "The reference must be unique!"),
    ]
