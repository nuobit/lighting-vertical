# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductFinish(models.Model):
    _name = "lighting.product.finish"
    _description = "Product Finish"
    _order = "code"

    code = fields.Char(
        required=True,
    )
    name = fields.Char(
        string="Description",
        required=True,
        translate=True,
    )
    html_color = fields.Char(
        string="HTML Color Index",
        help="Here you can set a specific HTML color index (e.g. #ff0000) "
        "to display the color on the website",
    )
    product_ids = fields.One2many(
        comodel_name="lighting.product",
        inverse_name="finish_id",
    )
    product2_ids = fields.One2many(
        comodel_name="lighting.product",
        inverse_name="finish2_id",
    )
    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
    )

    def _compute_product_count(self):
        for record in self:
            products = set(record.product_ids.ids + record.product2_ids.ids)
            record.product_count = len(products)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The finish name must be unique!"),
        ("code_uniq", "unique (code)", "The finish code must be unique!"),
    ]

    def name_get(self):
        vals = []
        for rec in self:
            name = "[%s] %s" % (rec.code, rec.name)
            vals.append((rec.id, name))
        return vals
