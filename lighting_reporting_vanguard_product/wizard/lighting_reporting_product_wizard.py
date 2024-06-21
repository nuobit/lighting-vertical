# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingReportingProductWizard(models.TransientModel):
    _inherit = "lighting.reporting.product.wizard"

    template = fields.Selection(
        selection_add=[("vanguard", "Vanguard")],
        ondelete={"vanguard": "cascade"},
        required=True,
    )

    def print_product_datasheet(self):
        if not self.template == "vanguard":
            return super().print_product_datasheet()
        data = {
            "ids": self.env.context.get("active_ids"),
            "model": self.env.context.get("active_model"),
            "lang": self.lang_id.code,
            "company": self.company_id.id,
        }
        return self.env.ref(
            "lighting_reporting_vanguard_product.report_product_vanguard_action"
        ).report_action(self, data=data)
