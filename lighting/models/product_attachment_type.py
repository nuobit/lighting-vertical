# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


# TODO: Name inconsistencies. Lighting_attachment_type is product_attachment?
#  It should be lighting.product.attachment.type
class LightingAttachmentType(models.Model):
    _name = "lighting.attachment.type"
    _description = "Product Attachment Type"
    _order = "sequence,code"

    def _sequence_default(self):
        max_sequence = (
            self.env["lighting.attachment.type"]
            .search([], order="sequence desc", limit=1)
            .sequence
        )

        return max_sequence + 1

    sequence = fields.Integer(
        required=True,
        default=_sequence_default,
        help="The sequence field is used to define order",
    )
    code = fields.Char(
        required=True,
    )
    name = fields.Char(
        string="Description",
        translate=True,
    )
    is_image = fields.Boolean(
        default=False,
    )
    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
    )

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env["lighting.product"].search_count(
                [("attachment_ids.type_id", "=", record.id)]
            )

    _sql_constraints = [
        (
            "name_uniq",
            "unique (code)",
            "The attachment type description must be unique!",
        ),
    ]

    def name_get(self):
        vals = []
        for rec in self:
            if rec.name:
                name = "%s (%s)" % (rec.name, rec.code)
            else:
                name = rec.code
            vals.append((rec.id, name))
        return vals
