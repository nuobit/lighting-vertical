# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class LightingETIMGroup(models.Model):
    _name = "lighting.etim.group"
    _order = "code"

    code = fields.Char(
        required=True,
    )
    name = fields.Char(
        string="Description",
        required=True,
        translate=True,
    )

    _sql_constraints = [
        ("code", "unique (code)", "The code must be unique!"),
    ]

    def name_get(self):
        vals = []
        for record in self:
            name = "[%s] %s" % (record.code, record.name)
            vals.append((record.id, name))

        return vals

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if args is None:
            args = []
        recs = self.search(
            ["|", ("code", operator, name), ("name", operator, name)] + args,
            limit=limit,
        )
        return recs.name_get()
