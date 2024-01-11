# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models


class LightingExport(models.TransientModel):
    _inherit = "lighting.export"

    output_type = fields.Selection(
        selection_add=[("export_product_xlsx", _("Excel file (.xlsx)"))],
        ondelete={"export_product_xlsx": "cascade"},
    )

    def export_product_xlsx(self):
        self.ensure_one()
        return {
            "type": "ir.actions.report",
            "report_name": "lighting_export_xlsx.export_product_xlsx",
            "report_type": "xlsx",
            "data": {
                "interval": self.interval,
                "hide_empty_fields": self.hide_empty_fields,
                "template_id": self.template_id.id,
                "active_ids": self.env.context.get("active_ids"),
                "lang": self.lang_id.code,
                "exclude_configurator": self.exclude_configurator,
            },
        }
