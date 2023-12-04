# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.lighting.models.product import C_STATES, D_MAP, ES_MAP

MIN_STOCK = 10


class LightingProduct(models.Model):
    _name = "lighting.product"
    _inherit = ["lighting.product", "lighting.seo.mixin"]

    website_published = fields.Boolean(
        string="Published on Website",
        copy=False,
        tracking=True,
    )

    website_published_readonly = fields.Boolean(
        compute="_compute_website_published_readonly",
    )

    def _compute_website_published_readonly(self):
        for rec in self:
            rec.website_published_readonly = not rec.user_has_groups(
                "lighting_seo.group_lighting_ecommerce_manager"
            )

    def website_publish_button(self):
        self.ensure_one()
        return self.write({"website_published": not self.website_published})

    seo_keyword_ids = fields.Many2many(
        relation="lighting_product_seo_keyword_rel",
        column1="product_id",
        column2="keyword_id",
    )
    marketplace_title = fields.Char(
        translate=True,
        tracking=True,
    )
    marketplace_description = fields.Text(
        translate=True,
        tracking=True,
    )

    def _check_state_marketing_stock(self, values):
        new_values = super(LightingProduct, self)._check_state_marketing_stock(values)
        values.update(new_values)
        current_state, new_state = self.state_marketing, values.get(
            "state_marketing", self.state_marketing
        )
        current_stock = self.available_qty + self.stock_future_qty
        new_stock = sum(
            [
                values[f] if f in values else self[f]
                for f in ("available_qty", "stock_future_qty")
            ]
        )
        if current_state in C_STATES:
            if new_state in D_MAP:
                self._update_with_check(new_values, "website_published", False)
        elif current_state in ES_MAP:
            if new_state == current_state:
                if new_stock > current_stock:
                    if new_stock >= MIN_STOCK:
                        self._update_with_check(new_values, "website_published", True)
            elif new_state == ES_MAP[current_state]:
                self._update_with_check(new_values, "website_published", False)
        elif current_state in D_MAP:
            if new_state == current_state:
                self._update_with_check(new_values, "website_published", False)
            elif new_state == D_MAP[current_state]:
                self._update_with_check(
                    new_values, "website_published", new_stock >= MIN_STOCK
                )
        return new_values

    def _check_website_published_readonly(self, vals):
        if "website_published" in vals:
            for rec in self:
                if rec.website_published_readonly:
                    raise ValidationError(
                        _(
                            "You have no permissions to modify the Website Published field"
                        )
                    )

    def write(self, vals):
        self._check_website_published_readonly(vals)
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._check_website_published_readonly(vals)
        return super().create(vals_list)
