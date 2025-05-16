# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models

from .tools import check_record_code_format


class LightingProductFinishType(models.Model):
    _name = "lighting.product.finish.type"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Product Finish Type"
    _order = "name"

    code = fields.Char(
        required=True,
        tracking=True,
    )
    name = fields.Char(
        required=True,
        translate=True,
        tracking=True,
    )

    @api.constrains("code")
    def _check_code(self):
        for rec in self:
            check_record_code_format(rec.code)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The finish type name must be unique!"),
        ("code_uniq", "unique (code)", "The finish type code must be unique!"),
    ]
