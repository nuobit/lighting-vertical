# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _, tools
from odoo.modules import get_module_resource
from odoo.exceptions import UserError, ValidationError

import base64
import requests

import io
from odoo.addons.queue_job.job import job

from PIL import Image

from odoo.tools import pycompat

import logging

_logger = logging.getLogger(__name__)


def is_known_image(base64_source):
    if not base64_source:
        return False
    try:
        image_stream = io.BytesIO(base64.b64decode(base64_source))
        Image.open(image_stream)
        return True
    except IOError:
        return False


def get_resized_images(base64_source, medium_name='image_medium', small_name='image_small',
                       medium_size=(500, 500), small_size=(64, 64),
                       encoding='base64', filetype=None):
    if isinstance(base64_source, pycompat.text_type):
        base64_source = base64_source.encode('ascii')

    return {
        medium_name: tools.image_resize_image(base64_source, medium_size, encoding, filetype, True),
        small_name: tools.image_resize_image(base64_source, small_size, encoding, filetype, True),
    }


class LightingAttachment(models.Model):
    _name = 'lighting.attachment'
    _order = 'sequence,id'

    def _sequence_default(self):
        max_sequence = self.env['lighting.attachment'] \
            .search([('product_id', '=', self.env.context.get('default_product_id'))],
                    order='sequence desc', limit=1).sequence

        return max_sequence + 1

    sequence = fields.Integer(required=True, default=_sequence_default,
                              help="The sequence field is used to define order")

    name = fields.Char(string='Description', translate=True)
    type_id = fields.Many2one(comodel_name='lighting.attachment.type', ondelete='restrict', required=True,
                              string='Type')

    datas_location = fields.Selection(
        string='Location',
        selection=[('file', 'File'), ('url', 'Url')],
        default='file',
        required=True
    )

    datas_url = fields.Char(string='Url')

    datas = fields.Binary(string="File", attachment=True)
    datas_fname = fields.Char(string='Filename')
    datas_size = fields.Char(string='Size', compute="_compute_datas_size", store=True)

    @api.depends('datas')
    def _compute_datas_size(self):
        for rec in self:
            if rec.datas_location == 'file':
                size = rec.attachment_id.file_size
                if size < 1000:
                    magn = 'Bytes'
                else:
                    size /= 1000
                    if size < 1000:
                        magn = 'Kb'
                    else:
                        size /= 1000
                        magn = 'Mb'

                if size - int(size) == 0.0:
                    rec.datas_size = "{:d} {}".format(int(size), magn)
                else:
                    rec.datas_size = "{:.2f} {}".format(size, magn)

    image_small = fields.Binary("Small-sized image", attachment=True, store=True, compute="_compute_images")
    image_medium = fields.Binary("Medium-sized image", attachment=True, store=True, compute="_compute_images")

    @api.depends('datas', 'datas_url', 'datas_location', 'type_id', 'type_id.is_image')
    def _compute_images(self):
        for rec in self:
            if rec.id:
                rec.regenerate_preview()

    image_known = fields.Boolean(
        string="Image Known", required=True,
        default=False, readonly=True, store=True, compute="_compute_known_image")

    @api.depends('datas', 'datas_url', 'datas_location', 'type_id', 'type_id.is_image')
    def _compute_known_image(self):
        for rec in self:
            rec.image_known = is_known_image(rec.get_datas())

    attachment_id = fields.Many2one(comodel_name='ir.attachment',
                                    compute='_compute_ir_attachment', readonly=True)

    @api.depends('datas')
    def _compute_ir_attachment(self):
        for rec in self:
            attachment_obj = rec.env['ir.attachment'] \
                .search([('res_field', '=', 'datas'),
                         ('res_id', '=', rec.id),
                         ('res_model', '=', rec._name)]) \
                .sorted('id', reverse=True)
            if attachment_obj:
                rec.attachment_id = attachment_obj[0]
            else:
                rec.attachment_id = False

    checksum = fields.Char(related='attachment_id.checksum', string='Checksum', readonly=True)

    public = fields.Boolean(related='attachment_id.public', string='Public')
    url = fields.Char(string='Url', compute='_compute_url', readonly=True)

    @api.depends('attachment_id', 'datas_url', 'datas_location')
    def _compute_url(self):
        for rec in self:
            rec.url = rec.url_get()

    date = fields.Date(string='Date')
    is_default = fields.Boolean(string='Default')

    lang_id = fields.Many2one(comodel_name='lighting.language', ondelete='restrict', string='Language')

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '%s (%s)' % (record.datas_fname, record.type_id.display_name)
            vals.append((record.id, name))

        return vals

    @api.constrains('datas_location', 'datas_url', 'datas', 'datas_fname')
    def _check_location_data_coherence(self):
        for rec in self:
            if rec.datas_location == 'file':
                if rec.datas_url:
                    raise ValidationError(
                        _("There's a Url defined and the location type is not 'Url'. "
                          "Please change the Location to 'Url' or clean the url data first"))
            elif rec.datas_location == 'url':
                if rec.datas or rec.datas_fname:
                    raise ValidationError(
                        _("There's a File defined and the location type is not 'File'. "
                          "Please change the Location to 'File' or clean the file data first"))

    def url_get(self, resolution=None, set_public=False):
        self.ensure_one()
        if self.datas_location == 'file':
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            pattern_l = ['%s/web/image/h/%s']
            if resolution:
                pattern_l.append(resolution)
            pattern_l.append('%s')

            if set_public and not self.attachment_id.public:
                self.sudo().attachment_id.public = True

            if self.attachment_id.checksum and self.datas_fname:
                return '/'.join(pattern_l) % (base_url, self.attachment_id.checksum, self.datas_fname)
            else:
                return False
        elif self.datas_location == 'url':
            return self.datas_url

        return False

    def _get_preview_images(self, datas):
        if datas:
            try:
                return get_resized_images(datas)
            except IOError:
                pass

            img_path = get_module_resource(
                'lighting', 'static/src/img',
                self.type_id.is_image and 'unknown_image.png' or 'document.png')
        else:
            img_path = get_module_resource('web', 'static/src/img', 'placeholder.png')

        if img_path:
            with open(img_path, 'rb') as f:
                return get_resized_images(base64.b64encode(f.read()))
        else:
            raise ValidationError(_("Thumbnail file for content type '%s' not found") % self.content_type)

    @api.multi
    def get_main_resized_image(self):
        images = self \
            .filtered(lambda x: x.image_known and x.type_id.is_image) \
            .sorted(lambda x: (x.type_id.sequence, x.sequence, x.id))
        if images:
            return {
                'image_medium': images[0].image_medium,
                'image_small': images[0].image_small,
            }

        img_path = get_module_resource('web', 'static/src/img', 'placeholder.png')
        if img_path:
            with open(img_path, 'rb') as f:
                return get_resized_images(base64.b64encode(f.read()))
        else:
            raise ValidationError(_("Thumbnail file 'placeholder.png' not found"))

    def get_datas(self):
        self.ensure_one()
        datas = None
        if self.datas_location == 'url' and self.datas_url:
            try:
                r = requests.get(self.datas_url, timeout=10)
            except Exception as e:
                raise UserError(_("Connection error accessing the Url '%s'\n\n%s") % (
                    self.datas_url, repr(e)
                ))
            else:
                if r.ok:
                    datas = base64.b64encode(r.content)
                else:
                    raise UserError(_("Data error '%i %s' accessing the URL '%s'") % (
                        r.status_code, r.reason, self.datas_url))
        elif self.datas_location == 'file' and self.datas:
            datas = self.datas

        return datas

    @api.multi
    def regenerate_preview(self):
        for rec in self:
            datas = rec.get_datas()
            rec.image_known = is_known_image(datas)
            resized_images = rec._get_preview_images(datas)
            rec.image_medium = resized_images['image_medium']
            rec.image_small = resized_images['image_small']

        return True
