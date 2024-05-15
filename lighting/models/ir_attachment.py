# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.model
    def get_attachment(self, record, res_field):
        return self.search(
            [
                ("res_id", "=", record.id),
                ("res_model", "=", record._name),
                ("res_field", "=", res_field),
            ],
        ).sorted("id", reverse=True)[:1]
