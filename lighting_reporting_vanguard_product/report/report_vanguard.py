# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright NuoBiT Solutions 2025 - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


# TODO:Review: Rename this model or file
class ProductReport(models.AbstractModel):
    _name = "report.lighting_reporting_vanguard_product.report_vanguard"
    _description = "Vanguard Product Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        model = "lighting.product"
        lang = self.env.lang
        company = self.env.company
        if data:
            if data.get("model"):
                model = data["model"]
            if data.get("ids"):
                docids = data["ids"]
            if data.get("lang"):
                lang = data["lang"]
            if data.get("company"):
                company = self.env["res.company"].browse(data["company"])
        docs = self.env[model].with_context(lang=lang).browse(docids)
        return {
            "doc_ids": docids,
            "doc_model": model,
            "docs": docs,
            "report_lang": lang,
            "report_company": company,
        }
