# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class LightingAttachmentType(models.Model):
    _name = "lighting.attachment.type"
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

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Description", translate=True)
    is_image = fields.Boolean(string="Is image", default=False)

    product_count = fields.Integer(
        compute="_compute_product_count", string="Product(s)"
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

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            if record.name:
                name = "%s (%s)" % (record.name, record.code)
            else:
                name = record.code

            vals.append((record.id, name))

        return vals
