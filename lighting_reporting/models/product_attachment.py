# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from PIL import Image, ImageChops, ImageEnhance
import io
import base64
from odoo.addons.queue_job.job import job


def autocrop(im, bgcolor):
    if im.mode != "RGB":
        if im.mode in ('P'):
            im = im.convert("RGBA")
            im2 = Image.new('RGB', im.size, bgcolor)
            im2.paste(im, (0, 0), im)
            im = im2
        im = im.convert("RGB")

    bg = Image.new("RGB", im.size, bgcolor)

    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return None  # no contents


def expand2square(im, bgcolor):
    width, height = im.size
    if width == height:
        return im
    elif width > height:
        result = Image.new(im.mode, (width, width), bgcolor)
        result.paste(im, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(im.mode, (height, height), bgcolor)
        result.paste(im, ((height - width) // 2, 0))
        return result


def resize(im, asked_size, by_side_long=False, allow_scale=True):
    if asked_size and asked_size != (None, None):
        im_size = im.size
        if by_side_long and im.size[0] < im.size[1]:
            im_size = (im_size[1], im_size[0])

        hw_ratio = im_size[1] / im_size[0]
        asked_width, asked_height = asked_size
        if asked_height is None:
            asked_height = int(float(asked_width) * hw_ratio)
        if asked_width is None:
            asked_width = int(float(asked_height) * 1 / hw_ratio)

        asked_size = asked_width, asked_height
        if im_size != asked_size:
            if by_side_long and im.size[0] < im.size[1]:
                asked_size = (asked_size[1], asked_size[0])
            if not allow_scale and (asked_size[0] > im.size[0] or asked_size[1] > im.size[1]):
                return im
            return im.resize(asked_size, Image.ANTIALIAS)

    return im


class LightingAttachment(models.Model):
    _inherit = 'lighting.attachment'

    is_datasheet = fields.Boolean(related='type_id.is_datasheet', readonly=True)

    last_update = fields.Datetime(string='Last Update', readonly=True)

    manual = fields.Boolean(string='Manual')

    @job(default_channel='root.lighting_datasheet')
    @api.model
    def generate_datasheet(self, attach_id):
        """ Generate product datasheet """
        attach = self.env['lighting.attachment'].browse(attach_id)
        if not attach.type_id.is_datasheet:
            raise ValidationError(_("You can only generate a datasheet if attachment type is datasheet"))
        if attach.manual:
            raise ValidationError(_("You cannot generate a datasheet if is manual"))

        attach.last_update = fields.Datetime.now()
        data = {
            'ids': attach.product_id.ids,
            'model': attach.product_id._name,
            'lang': attach.lang_id.code,
            'attach': attach,
        }
        pdfbin = self.env.ref('lighting_reporting.action_report_product') \
            .render_qweb_pdf(attach.product_id.ids, data=data)[0]

        family_name = attach.product_id.family_ids.mapped('name') and \
                      attach.product_id.family_ids.mapped('name')[0].upper() or None
        attach.write({
            'datas': base64.b64encode(pdfbin),
            'datas_fname': '%s.pdf' % '_'.join(
                filter(None, [attach.type_id.code, family_name, attach.product_id.reference])),
            'date': attach.last_update,
        })

    def get_optimized_image(self, enabled=True):
        if not enabled:
            return self.datas

        datas = base64.decodebytes(self.datas)
        im = Image.open(io.BytesIO(datas))

        im99 = resize(im, (500, None), by_side_long=True, allow_scale=False)

        # sharpener = ImageEnhance.Sharpness(im7)
        # im99 = sharpener.enhance(2.0)

        # im9 = autocrop(im7, (255, 255, 255))
        # if not im9:
        #     return self.datas
        #
        # im99 = expand2square(im9, (255, 255, 255))

        in_mem_file = io.BytesIO()
        im99.save(in_mem_file, format=im.format)

        datas_cropped = base64.b64encode(in_mem_file.getvalue())

        return datas_cropped
