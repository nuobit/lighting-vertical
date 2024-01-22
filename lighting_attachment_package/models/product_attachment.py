# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingAttachmentType(models.Model):
    _inherit = "lighting.attachment.type"

    package_ids = fields.One2many(
        string="Packages",
        comodel_name="lighting.attachment.package",
        inverse_name="type_id",
    )
