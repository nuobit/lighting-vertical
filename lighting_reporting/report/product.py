# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions 2025 - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


# TODO:Review: Rename this model or file
class ProductReport(models.AbstractModel):
    _name = "report.lighting_reporting.report_product"
    _description = "Lighting Product Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        model = "lighting.product"
        lang = self.env.lang
        if data:
            if data.get("model"):
                model = data["model"]
            if data.get("ids"):
                docids = data["ids"]
            if data.get("lang"):
                lang = data["lang"]
        docs = self.env[model].with_context(lang=lang).browse(docids)
        return {
            "doc_ids": docids,
            "doc_model": model,
            "docs": docs,
            "report_lang": lang,
        }
