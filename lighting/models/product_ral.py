# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductRal(models.Model):
    _name = "lighting.product.ral"
    _description = "Product RAL"
    _order = "code"
    _rec_names_search = ["name", "code"]

    code = fields.Char(
        required=True,
    )
    name = fields.Char(
        string="Description",
        required=True,
        translate=True,
    )
    product_ids = fields.One2many(
        comodel_name="lighting.product",
        inverse_name="ral_id",
    )
    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
    )

    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec.product_ids)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The ral name must be unique!"),
        ("code_uniq", "unique (code)", "The ral code must be unique!"),
    ]

    # TODO: Review this change
    # @api.model
    # def name_search(self, name, args=None, operator="ilike", limit=100):
    #     if args is None:
    #         args = []
    #     return self.search(
    #         ["|", ("code", operator, name), ("name", operator, name)] + args, limit=320
    #     ).name_get()

    def name_get(self):
        vals = []
        for rec in self:
            name = "[RAL %s] %s" % (rec.code, rec.name)
            vals.append((rec.id, name))
        return vals
