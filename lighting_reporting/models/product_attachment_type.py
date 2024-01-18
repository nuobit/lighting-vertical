# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingAttachmentType(models.Model):
    _inherit = "lighting.attachment.type"

    include_in_datasheet = fields.Boolean(string="Include in Datasheet")
