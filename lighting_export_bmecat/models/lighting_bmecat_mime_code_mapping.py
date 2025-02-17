# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class LightingBMEcatMimeCodeMapping(models.Model):
    _name = "lighting.bmecat.mime.code.mapping"
    _description = "Lighting BMEcat Mime Code Mapping"

    config_id = fields.Many2one(
        comodel_name="lighting.bmecat.config",
        required=True,
        ondelete="cascade",
    )
    mime_code_id = fields.Many2one(
        comodel_name="lighting.bmecat.mime.code", required=True
    )
    type_id = fields.Many2one(comodel_name="lighting.attachment.type", required=True)

    @api.constrains("code", "type_id", "config_id")
    def _check_unique_code_and_type(self):
        for rec in self:
            duplicate_code = self.search(
                [
                    ("config_id", "=", rec.config_id.id),
                    ("mime_code_id", "=", rec.mime_code_id.id),
                    ("id", "!=", rec.id),
                ]
            )
            if duplicate_code:
                raise ValidationError(
                    _("The MIME Code '%s' is already assigned to this BMEcat.")
                    % rec.code
                )
            duplicate_type = self.search(
                [
                    ("config_id", "=", rec.config_id.id),
                    ("type_id", "=", rec.type_id.id),
                    ("id", "!=", rec.id),
                ]
            )
            if duplicate_type:
                raise ValidationError(
                    _("The MIME Type '%s' is already assigned to this BMEcat.")
                    % rec.type_id.name
                )
