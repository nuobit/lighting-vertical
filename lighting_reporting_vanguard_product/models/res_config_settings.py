# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    product_template = fields.Selection(
        selection_add=[("vanguard", "Vanguard")],
        ondelete={"vanguard": "cascade"},
    )
