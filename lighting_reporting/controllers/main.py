# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import http
import base64
import werkzeug.exceptions

import logging

_logger = logging.getLogger(__name__)


class ProductDatasheetController(http.Controller):
    def generate_lighting_report(self, product_ids, lang_id=None):
        if not lang_id:
            lang_id = http.request.env.ref('base.lang_en')
        pdf = product_ids.get_product_datasheet(lang_id.id)

        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            # ('Content-Disposition', 'attachment; filename="picture.png"'),
            ('Content-Length', len(pdf)),
        ]
        return http.request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(['/web/datasheet/<string:reference>',
                 '/web/datasheet/<string:lang>/<string:reference>',
                 ], type='http', auth="user")
    def download_datasheet(self, lang=None, reference=None):
        # lang check
        lang_id = None
        if lang is not None:
            lang_id = http.request.env['res.lang'].search([
                ('active', '=', True),
                ('code', '=', lang),
            ])
            if len(lang_id) == 0:
                return werkzeug.exceptions.NotFound('The %s language does not exist' % lang)
            elif len(lang_id) > 1:
                return werkzeug.exceptions.InternalServerError('More than one language found with code %s' % lang)

        # reference check
        if reference is not None:
            product_id = http.request.env['lighting.product'].search([
                ('reference', '=', reference),
            ])
            if len(product_id) == 0:
                return werkzeug.exceptions.NotFound(
                    'The product with reference %s does not exist' % reference)
            elif len(product_id) > 1:
                return werkzeug.exceptions.InternalServerError(
                    'More than one product found with reference %s' % reference)
        else:
            return werkzeug.exceptions.BadRequest('A reference must be provided')

        return self.generate_lighting_report(product_id, lang_id)

    @http.route(['/web/datasheets/<int:lang_id>/<string:product_ids>',
                 ], type='http', auth="user")
    def download_datasheets(self, lang_id, product_ids, *args, **kwargs):
        # lang check
        if lang_id:
            lang = http.request.env['res.lang'].search([
                ('id', '=', lang_id),
            ])
            if not lang:
                return werkzeug.exceptions.NotFound('The %s language does not exist' % lang)
        else:
            return werkzeug.exceptions.BadRequest('A language id must be provided')

        # product check
        if product_ids is not None:
            product_ids = http.request.env['lighting.product'].browse(
                [int(x) for x in product_ids.split(',')])
        else:
            return werkzeug.exceptions.BadRequest("Product id's must be provided")

        return self.generate_lighting_report(product_ids, lang)
