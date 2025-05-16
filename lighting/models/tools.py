# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import re

from odoo import _
from odoo.exceptions import ValidationError


def check_record_code_format(code):
    m = re.match("^[a-z0-9_]+$", code)
    if not m:
        raise ValidationError(
            _("Code must be only lowercase letters, numbers, or underscores.")
        )
