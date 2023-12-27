# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductFamily(models.Model):
    _inherit = "lighting.product.family"

    no_templates = fields.Boolean(
        help="Enabled if this family is NOT allowed to "
        "contain templates (products with variants)",
    )
