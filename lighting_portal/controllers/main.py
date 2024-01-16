import base64

from odoo import http

import werkzeug.exceptions

import logging

_logger = logging.getLogger(__name__)


class ProductDatasheetController(http.Controller):
    def get_products_xml(self, lang=None):
        # lang check
        if not lang:
            lang = 'es_ES'

        lang_id = http.request.env['res.lang'].search([
            ('active', '=', True),
            ('code', '=', lang),
        ])
        if len(lang_id) == 0:
            return werkzeug.exceptions.NotFound('The %s language does not exist' % lang)
        elif len(lang_id) > 1:
            return werkzeug.exceptions.InternalServerError('More than one language found with code %s' % lang)

        # generate report
        report = http.request.env.ref('lighting_portal.action_report_product_xml')
        product_ids = http.request.env['lighting.portal.product'].search([]) \
            .sorted(lambda x: x.reference).mapped('id')
        xml_products = report.with_context(lang=lang).render_qweb_xml(product_ids, {})[0]

        # return report
        xmlhttpheaders = [
            ('Content-Type', 'application/xml'),
            ('Content-Length', len(xml_products)),
        ]
        return http.request.make_response(xml_products, headers=xmlhttpheaders)

    @http.route(['/services/products',
                 '/services/<string:lang>/products',
                 ], type='http', auth="none")
    def download_products_xml(self, lang=None):
        # Check for Odoo session authentication
        if http.request.session.uid:
            http.request.uid = http.request.session.uid
            return self.get_products_xml(lang)

        # Check for HTTP Basic Authentication
        headers = http.request.httprequest.headers
        basic_auth_header = headers.get('Authorization')
        if basic_auth_header:
            try:
                auth_type, encoded_credentials = basic_auth_header.split(None, 1)
                if auth_type.lower() != 'basic':
                    raise werkzeug.exceptions.Unauthorized('Unsupported authentication method')
                username, password = base64.b64decode(encoded_credentials).decode().split(':', 1)
            except Exception as e:
                msg = "Error processing authentication"
                _logger.error(msg + f": {e}")
                raise werkzeug.exceptions.BadRequest(msg)
            uid = http.request.session.authenticate(http.request.session.db, username, password)
            if not uid:
                raise werkzeug.exceptions.Unauthorized('Invalid credentials')
            return self.get_products_xml(lang)

        # No authentication
        raise werkzeug.exceptions.Unauthorized('Invalid authentication')
