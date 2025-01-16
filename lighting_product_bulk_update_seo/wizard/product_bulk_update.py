# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductBulkUpdate(models.TransientModel):
    _inherit = "lighting.product.bulk.update"

    website_published = fields.Boolean(string="Published on Website")

    def _get_product_bulk_update_values(self):
        values = super()._get_product_bulk_update_values()
        values.update(
            {
                "website_published": self.website_published,
            }
        )
        return values
