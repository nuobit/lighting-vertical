# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import UserError


class LightingProductGroupType(models.Model):
    _name = "lighting.product.group.type"
    _description = "Product Group Type"
    _order = "name"

    code = fields.Char(
        required=True,
    )
    name = fields.Char(
        required=True,
    )
    group_count = fields.Integer(
        compute="_compute_group_count",
        string="Group(s)",
    )

    def _compute_group_count(self):
        for rec in self:
            rec.group_count = self.env["lighting.product.group"].search_count(
                [("type_ids", "=", rec.id)]
            )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The name must be unique!"),
        ("code_uniq", "unique (code)", "The code must be unique!"),
    ]

    def unlink(self):
        records = self.env["lighting.product.group"].search(
            [("type_ids", "in", self.ids)]
        )
        if records:
            raise UserError(
                _("You are trying to delete a record that is still referenced!")
            )
        return super().unlink()
