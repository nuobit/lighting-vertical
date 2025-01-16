# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductBulkUpdate(models.TransientModel):
    _name = "lighting.product.bulk.update"
    _description = "Bulk Update for Products"

    state_marketing = fields.Selection(
        selection=lambda self: self.env["lighting.product"]
        ._fields["state_marketing"]
        .selection,
    )

    def _get_product_bulk_update_values(self):
        return {
            "state_marketing": self.state_marketing,
        }

    def apply_and_close_product_bulk_update(self):
        self.ensure_one()
        self.env["lighting.product"].browse(self.env.context.get("active_ids")).write(
            self._get_product_bulk_update_values()
        )
        return {"type": "ir.actions.act_window_close"}
