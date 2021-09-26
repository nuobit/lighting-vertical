# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

import werkzeug.exceptions

from odoo import http

_logger = logging.getLogger(__name__)


class LightingExportJsonController(http.Controller):
    @http.route(['/lighting/export/<string:code>/<string:object>/<string:lang>',
                 ], type='http', auth="public")
    def export_template(self, code=None, object=None, lang=None):
        # get language
        lang_id = None
        if lang is not None:
            lang_id = http.request.env['res.lang'].sudo().search([
                ('active', '=', True),
                ('code', '=', lang),
            ])
            if len(lang_id) == 0:
                return werkzeug.exceptions.NotFound('The %s language does not exist' % lang)
            elif len(lang_id) > 1:
                return werkzeug.exceptions.InternalServerError('More than one language found with code %s' % lang)

        # get template
        tmpl = http.request.env['lighting.export.template'].sudo().search([
            ('link_enabled', '=', True),
            ('lang_ids', 'in', lang_id.ids),
            ('code', '=', code),
        ])
        if not tmpl:
            return werkzeug.exceptions.NotFound("Template %s not found or not enabled for the language selected %s" % (
                code, lang_id.code))
        if len(tmpl) > 1:
            return werkzeug.exceptions.InternalServerError(
                'More than one template found with code %s and language' % (code, lang_id.code))

        # check objects
        if object not in tmpl._VALID_OBJECTS:
            return werkzeug.exceptions.NotFound(
                'Resource %s not valid' % (object,))

        # check authentication
        if tmpl.link_auth_enabled:
            auth = http.request.httprequest.authorization
            if not auth or not isinstance(auth, dict):
                return werkzeug.exceptions.Forbidden('Invalid credentials')
            username, password = auth.get('username', None), auth.get('password', None)
            if any([
                not username,
                not password,
                tmpl.link_username != username,
                tmpl.link_password != password
            ]):
                return werkzeug.exceptions.Forbidden('Invalid credentials')

        # read the resource
        filename = tmpl.get_full_filepath(object, lang_id.code)
        try:
            with open(filename, 'r') as f:
                file_content = f.read()
        except FileNotFoundError as e:
            return werkzeug.exceptions.NotFound(
                'Resource %s not found' % (object,))

        return http.request.make_response(file_content,
                                          [('Content-Type', 'application/json'),
                                           ])
