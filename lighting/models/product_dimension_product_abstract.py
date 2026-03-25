# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LightingProductDimensionProductAbstract(models.AbstractModel):
    _name = "lighting.product.dimension.product.abstract"
    _inherit = "lighting.product.dimension.abstract"
    _description = "Product Dimension Product Abstract"

    product_id = fields.Many2one(
        comodel_name="lighting.product",
        ondelete="cascade",
        index=True,
    )

    @api.constrains("type_id", "product_id")
    def _check_duplicated_dimension(self):
        for rec in self:
            others = self.search(
                [
                    ("product_id", "=", rec.product_id.id),
                    ("type_id", "=", rec.type_id.id),
                    ("id", "!=", rec.id),
                ]
            )
            if others:
                raise ValidationError(
                    _("The dimension %s is duplicated") % rec.type_id.name
                )
