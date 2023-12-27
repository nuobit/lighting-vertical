# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class LightingETIMClass(models.Model):
    _name = "lighting.etim.class"
    _order = "code"

    code = fields.Char(
        required=True,
    )
    name = fields.Char(
        string="Description",
        required=True,
        translate=True,
    )
    version = fields.Integer(
        required=True,
    )
    change_code = fields.Char(
        required=True,
    )
    status = fields.Char(
        required=True,
    )
    group_id = fields.Many2one(
        comodel_name="lighting.etim.group",
        ondelete="restrict",
        required=True,
    )
    synonim_ids = fields.One2many(
        comodel_name="lighting.etim.class.synonim",
        inverse_name="class_id",
        string="Synonims",
    )
    feature_ids = fields.One2many(
        comodel_name="lighting.etim.class.feature",
        inverse_name="class_id",
        string="Features",
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
