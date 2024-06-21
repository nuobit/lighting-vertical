# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

import werkzeug.exceptions

from odoo import http

_logger = logging.getLogger(__name__)


class ProductDatasheetController(http.Controller):
    def generate_lighting_report(self, company, template, product_id, lang_id=None):
        """Generate the datasheet report for the product"""
        return NotImplementedError

    def extract_params(self, param1, param2):
        """Extract the language and template from the URL"""
        template_values = dict(
            http.request.env["res.config.settings"]
            ._fields["product_template"]
            .selection
        )
        lang = http.request.env["res.lang"].search(
            [
                ("active", "=", True),
                ("code", "=", param2 or param1),
            ]
        )
        template = (
            http.request.env["ir.config_parameter"]
            .sudo()
            .get_param("lighting_reporting_product.product_template")
        )
        if not template:
            raise werkzeug.exceptions.InternalServerError(
                "The template default value is not defined"
            )
        if param2 is not None:
            if len(lang) == 0:
                raise werkzeug.exceptions.NotFound(
                    "The %s language does not exist" % param2
                )
            elif len(lang) > 1:
                raise werkzeug.exceptions.InternalServerError(
                    "More than one language found with code %s" % param2
                )
            elif param1 not in template_values:
                raise werkzeug.exceptions.InternalServerError(
                    "The template %s does not exist" % param1
                )
            return param1, lang
        elif param1 is not None:
            if param1 in template_values:
                return param1, None
            elif len(lang) == 1:
                return template, lang
        return template, None

    def get_company(self, company_id):
        """Get the company from the URL"""
        domain = [("id", "=", http.request.env.user.company_id.id)]
        if company_id is not None:
            domain = [("id", "=", company_id)]
        company = http.request.env["res.company"].search(domain)
        if len(company) == 0:
            raise werkzeug.exceptions.NotFound(
                "The company with id %s does not exist" % company_id
            )
        return company

    @http.route(
        [
            "/web/datasheet/<string:reference>",
            "/web/datasheet/<string:param1>/<string:reference>",
            "/web/datasheet/<int:company_id>/<string:reference>",
            "/web/datasheet/<int:company_id>/<string:param1>/<string:reference>",
            "/web/datasheet/<string:param1>/<string:param2>/<string:reference>",
            "/web/datasheet/<int:company_id>/<string:param1>/<string:param2>"
            "/<string:reference>",
        ],
        type="http",
        auth="user",
    )
    def download_datasheet(
        self, company_id=None, param1=None, param2=None, reference=None
    ):
        company = self.get_company(company_id)
        template, lang = self.extract_params(param1, param2)

        # reference check
        if reference is not None:
            product_id = http.request.env["lighting.product"].search(
                [
                    ("reference", "=", reference),
                ]
            )
            if len(product_id) == 0:
                return werkzeug.exceptions.NotFound(
                    "The product with reference %s does not exist" % reference
                )
            elif len(product_id) > 1:
                return werkzeug.exceptions.InternalServerError(
                    "More than one product found with reference %s" % reference
                )
        else:
            return werkzeug.exceptions.BadRequest("A reference must be provided")

        return self.generate_lighting_report(company, template, product_id, lang)
