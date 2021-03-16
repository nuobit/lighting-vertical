# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from PIL import Image, ImageChops, ImageEnhance
import io
import base64
from odoo.addons.queue_job.job import job


class LightingAttachmentType(models.Model):
    _inherit = 'lighting.attachment.type'

    is_datasheet = fields.Boolean(string="Is Datasheet")
