# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import http

from odoo.addons.lighting_reporting_product.controllers.main import (
    ProductDatasheetController,
)

_logger = logging.getLogger(__name__)


class ProductDatasheetController(ProductDatasheetController):
    def generate_lighting_report(self, company, template, product_id, lang_id=None):
        if template != "vanguard":
            return super().generate_lighting_report(
                company, template, product_id, lang_id
            )
        data = {
            "model": product_id._name,
            "ids": product_id.ids,
            "lang": lang_id and lang_id.code or None,
            "company": company.id,
        }
        pdf, _ = http.request.env.ref(
            "lighting_reporting_vanguard_product.report_product_vanguard_action"
        )._render_qweb_pdf(
            "lighting_reporting_vanguard_product.report_product_vanguard_action",
            data=data,
        )
        pdfhttpheaders = [
            ("Content-Type", "application/pdf"),
            ("Content-Length", len(pdf)),
        ]
        return http.request.make_response(pdf, headers=pdfhttpheaders)
