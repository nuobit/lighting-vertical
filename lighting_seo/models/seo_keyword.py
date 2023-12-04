# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import UserError


class LightingSEOKeyword(models.Model):
    _name = "lighting.seo.keyword"
    _order = "name"

    name = fields.Char(
        string="Keyword",
        required=True,
        translate=True,
    )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The keyword must be unique!"),
    ]

    product_count = fields.Integer(
        string="Product(s)",
        compute="_compute_counts",
    )
    family_count = fields.Integer(
        string="Family(s)",
        compute="_compute_counts",
    )
    category_count = fields.Integer(
        string="Categories(s)",
        compute="_compute_counts",
    )
    application_count = fields.Integer(
        string="Application(s)",
        compute="_compute_counts",
    )
    catalog_count = fields.Integer(
        string="Catalog(s)",
        compute="_compute_counts",
    )

    def _compute_counts(self):
        maps = [
            ("product_count", "lighting.product"),
            ("family_count", "lighting.product.family"),
            ("category_count", "lighting.product.category"),
            ("application_count", "lighting.product.application"),
            ("catalog_count", "lighting.catalog"),
        ]
        for rec in self:
            for field, model in maps:
                count = self.env[model].search_count([("seo_keyword_ids", "=", rec.id)])
                setattr(rec, field, count)

    all_product_count = fields.Integer(
        string="All product(s)",
        compute="_compute_all_product_count",
    )

    def _compute_all_product_count(self):
        maps = [
            ("id", "lighting.product"),
            ("family_ids", "lighting.product.family"),
            ("category_id", "lighting.product.category"),
            ("application_ids", "lighting.product.application"),
            ("catalog_ids", "lighting.catalog"),
        ]
        for rec in self:
            product_ids = set()
            for field, model in maps:
                ids = (
                    rec.env[model]
                    .search([("seo_keyword_ids", "=", rec.id)])
                    .mapped("id")
                )
                product_ids.update(
                    rec.env["lighting.product"].search([(field, "in", ids)])
                )
            rec.all_product_count = len(product_ids)

    def unlink(self):
        models = [
            "lighting.product",
            "lighting.catalog",
            "lighting.product.family",
            "lighting.product.application",
        ]

        for model in models:
            records = self.env[model].search([("seo_keyword_ids", "in", self.ids)])
            if records:
                raise UserError(
                    _(
                        "You are trying to delete a record "
                        "that is still referenced by '%s' model!" % model
                    )
                )

        return super(LightingSEOKeyword, self).unlink()
