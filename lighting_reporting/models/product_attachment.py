# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import base64
import io

from PIL import Image, ImageChops

from odoo import models


def autocrop(im, bgcolor):
    if im.mode != "RGB":
        if im.mode in ("P"):
            im = im.convert("RGBA")
            im2 = Image.new("RGB", im.size, bgcolor)
            im2.paste(im, (0, 0), im)
            im = im2
        im = im.convert("RGB")

    bg = Image.new("RGB", im.size, bgcolor)

    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return None  # no contents


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
            if not allow_scale and (
                asked_size[0] > im.size[0] or asked_size[1] > im.size[1]
            ):
                return im
            return im.resize(asked_size, Image.ANTIALIAS)

    return im


class LightingAttachment(models.Model):
    _inherit = "lighting.attachment"

    # TODO: review this function.
    def get_optimized_image(self, enabled=True):
        datas = self.get_datas()
        if not enabled or not datas:
            return datas
        datas_bin = base64.decodebytes(datas)
        im = Image.open(io.BytesIO(datas_bin))
        # TODO: Can we use a new images?
        im99 = resize(im, (500, None), by_side_long=True, allow_scale=False)
        in_mem_file = io.BytesIO()
        im99.save(in_mem_file, format=im.format)
        datas_cropped = base64.b64encode(in_mem_file.getvalue())
        return datas_cropped
