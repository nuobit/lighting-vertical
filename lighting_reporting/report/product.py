# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ProductReport(models.AbstractModel):
    _name = 'report.lighting_reporting.report_product'

    @api.model
    def get_report_values(self, docids, data=None):
        model = 'lighting.product'
        lang = self.env.lang
        if data:
            model = data['model']
            docids = data['ids']
            lang = data['lang']
            attach = data['attach']

        docs = self.env[model].with_context(lang=lang).browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': model,
            'docs': docs,
            'lang': lang,
            'attach': attach,
        }
