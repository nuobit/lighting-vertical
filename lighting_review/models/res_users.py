# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _


class Users(models.Model):
    _inherit = 'res.users'

    review_mode = fields.Boolean(string="Review mode", help="Enable or disable review mode",
                                 default=False)
