# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Users(models.Model):
    _inherit = "res.users"

    review_mode = fields.Boolean(
        help="Enable or disable review mode",
        default=False,
    )
