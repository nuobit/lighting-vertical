# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError

# TODO: Name inconsistencies. Lighting_catalog is product_catalog?
#  It should be lighting.product.catalog?.


class LightingCatalog(models.Model):
    _name = "lighting.catalog"
    _description = "Product Catalog"
    _inherit = "image.mixin"
    _order = "name"

    name = fields.Char(
        string="Catalog",
        required=True,
    )
    description_show_ip = fields.Boolean(
        string="Description show IP",
        help="If checked, IP and IP2 will be shown on a generated product description "
        "for every product in this catalog",
    )
    description_show_ip_condition = fields.Char(
        string="Show IP condition",
        help="Condition that defines what IP's will be shown on the "
        "description "
        "in this catalog. Example: %(value)s > 'IP20' and %(value)s < "
        "'IP60'",
    )
    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
    )

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env["lighting.product"].search_count(
                [("catalog_ids", "=", record.id)]
            )

    # image: all image fields are base64 encoded and PIL-supported
    # TODO:MigrationScript

    # image = fields.Binary(
    #     attachment=True,
    #     help="This field holds the image used as "
    #     "image for the product, limited to 1024x1024px.",
    # )
    # image_medium = fields.Binary(
    #     string="Medium-sized image",
    #     attachment=True,
    #     help="Medium-sized image of the product. It is automatically "
    #     "resized as a 128x128px image, with aspect ratio preserved, "
    #     "only when the image exceeds one of those sizes. "
    #     "Use this field in form views or some kanban views.",
    # )
    # image_small = fields.Binary(
    #     string="Small-sized image",
    #     attachment=True,
    #     help="Small-sized image of the product. It is automatically "
    #     "resized as a 64x64px image, with aspect ratio preserved. "
    #     "Use this field anywhere a small image is required.",
    # )

    html_color = fields.Char(
        string="HTML Color Index",
        help="Here you can set a specific HTML color index (e.g. #ff0000) "
        "to display the color on the website",
    )

    color = fields.Integer(
        string="Color Index",
    )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The name of catalog must be unique!"),
    ]

    # TODO: REVIEW: this function image_resize_images don't exist in tools.
    @api.model_create_multi
    def create(self, vals_list):
        # tools.image_resize_images(vals_list)
        res = super().create(vals_list)
        return res

    def write(self, values):
        # tools.image_resize_images(values)
        res = super().write(values)
        return res

    def unlink(self):
        records = self.env["lighting.product"].search([("catalog_ids", "in", self.ids)])
        if records:
            raise UserError(
                _("You are trying to delete a record that is still referenced!")
            )
        return super(LightingCatalog, self).unlink()
