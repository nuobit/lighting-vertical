# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class LightingAttachmentType(models.Model):
    _inherit = "lighting.attachment.type"

    is_import_file_policy_variable = fields.Boolean(
        help="If checked, during the import attachment process, you can choose "
        "whether to add a new imported file or overwrite the existing one. "
        "This allows flexibility in handling multiple file imports."
    )

    @api.constrains("is_import_file_policy_variable")
    def _check_is_import_file_policy_variable(self):
        for rec in self:
            if not rec.allow_multiple_files:
                raise ValidationError(
                    _(
                        "To set the import file policy variable, you must allow "
                        "multiple files."
                    )
                )
