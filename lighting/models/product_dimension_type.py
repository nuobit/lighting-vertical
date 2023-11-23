# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingDimensionType(models.Model):
    _name = "lighting.dimension.type"
    _description = "Product Dimension Type"
    _order = "name"

    name = fields.Char(
        required=True,
        translate=True,
    )
    code = fields.Char(
        help="Code used to identify the dimension type",
    )
    uom = fields.Char(
        help="Unit of measure",
    )
    description = fields.Char(
        string="Internal description",
    )
    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
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

    def name_get(self):
        vals = []
        for rec in self:
            name_l = [rec.name]
            if rec.uom:
                name_l.append("(%s)" % rec.uom)
            vals.append((rec.id, " ".join(name_l)))

        return vals
