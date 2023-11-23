# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import base64
import io
import logging

import requests
from PIL import Image

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_resource_path

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


# TODO: Name inconsistencies. Lighting_attachment is product_attachment?
#  It should be lighting.product.attachment.
class LightingAttachment(models.Model):
    _name = "lighting.attachment"
    _description = "Product Attachment"
    _order = "sequence,id"

    def _sequence_default(self):
        max_sequence = (
            self.env["lighting.attachment"]
            .search(
                [("product_id", "=", self.env.context.get("default_product_id"))],
                order="sequence desc",
                limit=1,
            )
            .sequence
        )

        return max_sequence + 1

    sequence = fields.Integer(
        required=True,
        default=_sequence_default,
        help="The sequence field is used to define order",
    )
    name = fields.Char(
        string="Description",
        translate=True,
    )
    type_id = fields.Many2one(
        comodel_name="lighting.attachment.type",
        ondelete="restrict",
        required=True,
    )
    datas_location = fields.Selection(
        string="Location",
        selection=[("file", "File"), ("url", "Url")],
        default="file",
        required=True,
    )
    datas_url = fields.Char(
        string="Url",
    )
    datas = fields.Binary(
        string="File",
        attachment=True,
    )
    datas_fname = fields.Char(
        string="Filename",
    )
    datas_size = fields.Char(
        string="Size",
        compute="_compute_datas_size",
        store=True,
    )

    @api.depends("datas")
    def _compute_datas_size(self):
        for rec in self:
            if rec.datas_location == "file":
                size = rec.attachment_id.file_size
                if size < 1000:
                    magn = "Bytes"
                else:
                    size /= 1000
                    if size < 1000:
                        magn = "Kb"
                    else:
                        size /= 1000
                        magn = "Mb"

                if size - int(size) == 0.0:
                    rec.datas_size = "{:d} {}".format(int(size), magn)
                else:
                    rec.datas_size = "{:.2f} {}".format(size, magn)
            else:
                rec.datas_size = False

    image_small = fields.Image(
        string="Small-sized image",
        attachment=True,
        max_width=128,
        max_height=128,
        store=True,
        compute="_compute_images",
    )
    image_medium = fields.Binary(
        string="Medium-sized image",
        attachment=True,
        max_width=512,
        max_height=512,
        store=True,
        compute="_compute_images",
    )

    @api.depends("datas", "datas_url", "datas_location", "type_id", "type_id.is_image")
    def _compute_images(self):
        for rec in self:
            if rec.id:
                rec.regenerate_preview()

    image_known = fields.Boolean(
        required=True,
        default=False,
        readonly=True,
        store=True,
        compute="_compute_known_image",
    )

    @api.depends("datas", "datas_url", "datas_location", "type_id", "type_id.is_image")
    def _compute_known_image(self):
        for rec in self:
            rec.image_known = is_known_image(rec.get_datas())

    attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        compute="_compute_ir_attachment",
        readonly=True,
    )

    @api.depends("datas")
    def _compute_ir_attachment(self):
        for rec in self:
            attachment_obj = (
                rec.env["ir.attachment"]
                .search(
                    [
                        ("res_field", "=", "datas"),
                        ("res_id", "=", rec.id),
                        ("res_model", "=", rec._name),
                    ]
                )
                .sorted("id", reverse=True)
            )
            if attachment_obj:
                rec.attachment_id = attachment_obj[0]
            else:
                rec.attachment_id = False

    checksum = fields.Char(
        related="attachment_id.checksum",
    )
    public = fields.Boolean(
        compute="_compute_public",
        readonly=False,
    )

    @api.depends("attachment_id", "attachment_id.public")
    def _compute_public(self):
        for rec in self:
            rec.public = rec.attachment_id.public

    url = fields.Char(
        compute="_compute_url",
        readonly=True,
    )

    @api.depends("attachment_id", "datas_url", "datas_location")
    def _compute_url(self):
        for rec in self:
            rec.url = rec.url_get()

    date = fields.Date()
    is_default = fields.Boolean(
        string="Default",
    )
    lang_id = fields.Many2one(
        comodel_name="lighting.language",
        ondelete="restrict",
        string="Language",
    )
    product_id = fields.Many2one(
        comodel_name="lighting.product",
        ondelete="cascade",
    )

    def name_get(self):
        vals = []
        for record in self:
            name = "%s (%s)" % (record.datas_fname, record.type_id.display_name)
            vals.append((record.id, name))

        return vals

    @api.constrains("datas_location", "datas_url", "datas", "datas_fname")
    def _check_location_data_coherence(self):
        for rec in self:
            if rec.datas_location == "file":
                if rec.datas_url:
                    raise ValidationError(
                        _(
                            "There's a Url defined and the location type is not 'Url'. "
                            "Please change the Location to 'Url' or clean the url data first"
                        )
                    )
            elif rec.datas_location == "url":
                if rec.datas or rec.datas_fname:
                    raise ValidationError(
                        _(
                            "There's a File defined and the location type is not 'File'. "
                            "Please change the Location to 'File' or clean the file data first"
                        )
                    )

    def url_get(self, resolution=None, set_public=False):
        self.ensure_one()
        if self.datas_location == "file":
            base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            pattern_l = ["%s/web/image/h/%s"]
            if resolution:
                pattern_l.append(resolution)
            pattern_l.append("%s")

            if set_public and not self.attachment_id.public:
                self.sudo().attachment_id.public = True

            if self.attachment_id.checksum and self.datas_fname:
                return "/".join(pattern_l) % (
                    base_url,
                    self.attachment_id.checksum,
                    self.datas_fname,
                )
            else:
                return False
        elif self.datas_location == "url":
            return self.datas_url

        return False

    def get_main_resized_image(self):
        images = self.filtered(lambda x: x.image_known and x.type_id.is_image).sorted(
            lambda x: (x.type_id.sequence, x.sequence, x.id)
        )
        if images:
            return {
                "image_medium": images[0].image_medium,
                "image_small": images[0].image_small,
            }

        img_path = get_resource_path("web", "static/img", "placeholder.png")
        if img_path:
            image = base64.b64encode(open(img_path, "rb").read())
            return {
                "image_medium": image,
                "image_small": image,
            }
        else:
            raise ValidationError(_("Thumbnail file 'placeholder.png' not found"))

    def get_datas(self):
        self.ensure_one()
        datas = None
        if self.datas_location == "url" and self.datas_url:
            try:
                r = requests.get(self.datas_url, timeout=10)
            except Exception as e:
                raise UserError(
                    _("Connection error accessing the Url '%(url)s'\n\n%(message)s")
                    % {
                        "url": self.datas_url,
                        "message": repr(e),
                    }
                ) from e
            else:
                if r.ok:
                    datas = base64.b64encode(r.content)
                else:
                    raise UserError(
                        _(
                            "Data error '%(code)i %(reason)s' accessing the URL '%(url)s'"
                        )
                        % {
                            "code": r.status_code,
                            "reason": r.reason,
                            "url": self.datas_url,
                        }
                    )
        elif self.datas_location == "file" and self.datas:
            datas = self.datas

        return datas

    def regenerate_preview(self):
        for rec in self:
            datas = rec.get_datas()
            rec.image_known = is_known_image(datas)
            if datas:
                try:
                    image_stream = io.BytesIO(base64.b64decode(datas))
                    Image.open(image_stream)
                    rec.image_medium = datas
                    rec.image_small = datas
                except IOError:
                    img_path = get_resource_path(
                        "lighting",
                        "static/src/img",
                        self.type_id.is_image and "unknown_image.png" or "document.png",
                    )
                    rec.image_medium = base64.b64encode(open(img_path, "rb").read())
                    rec.image_small = base64.b64encode(open(img_path, "rb").read())
            else:
                img_path = get_resource_path("web", "static/img", "placeholder.png")
                rec.image_medium = base64.b64encode(open(img_path, "rb").read())
                rec.image_small = base64.b64encode(open(img_path, "rb").read())

        return True
