# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright NuoBiT 2025 - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductBulkUpdate(models.TransientModel):
    _name = "lighting.product.bulk.update"
    _description = "Bulk Update for Products"

    state_enabled = fields.Boolean()
    state = fields.Selection(
        selection=lambda self: self.env["lighting.product"]._fields["state"].selection,
    )

    state_marketing_enabled = fields.Boolean()
    state_marketing = fields.Selection(
        selection=lambda self: self.env["lighting.product"]
        ._fields["state_marketing"]
        .selection,
    )

    def _get_product_bulk_update_values(self):
        values = {}
        if self.state_enabled:
            values["state"] = self.state
        if self.state_marketing_enabled:
            values["state_marketing"] = self.state_marketing
        return values

    def apply_and_close_product_bulk_update(self):
        self.ensure_one()
        values = self._get_product_bulk_update_values()
        if values:
            self.env["lighting.product"].browse(
                self.env.context.get("active_ids")
            ).write(values)
        return {"type": "ir.actions.act_window_close"}
