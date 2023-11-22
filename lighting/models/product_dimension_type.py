# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class LightingDimensionType(models.Model):
    _name = "lighting.dimension.type"
    _order = "name"

    name = fields.Char(string="Name", required=True, translate=True)
    code = fields.Char(string="Code", help="Code used to identify the dimension type")
    uom = fields.Char(string="Uom", help="Unit of mesure")
    description = fields.Char(string="Internal description")

    product_count = fields.Integer(
        compute="_compute_product_count", string="Product(s)"
    )

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env["lighting.product"].search_count(
                [
                    "|",
                    "|",
                    ("dimension_ids.type_id", "=", record.id),
                    ("recess_dimension_ids.type_id", "=", record.id),
                    ("beam_ids.dimension_ids.type_id", "=", record.id),
                ]
            )

    _sql_constraints = [
        ("name_uniq", "unique (name, uom)", "The dimension name must be unique!"),
        ("code_uniq", "unique (code)", "The dimension code must be unique!"),
    ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name_l = [record.name]
            if record.uom:
                name_l.append("(%s)" % record.uom)
            vals.append((record.id, " ".join(name_l)))

        return vals
