# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


# TODO: Rename this models
class LightingProductNotes(models.Model):
    _name = "lighting.product.notes"
    _description = "Product Notes"
    _rec_name = "note_id"
    _order = "product_id,sequence desc"

    sequence = fields.Integer(
        required=True,
        default=1,
    )
    note_id = fields.Many2one(
        comodel_name="lighting.product.note",
        ondelete="restrict",
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name="lighting.product",
        ondelete="cascade",
        required=True,
    )

    _sql_constraints = [
        (
            "name_uniq",
            "unique (product_id,note_id)",
            "There's notes used more than one time!",
        ),
    ]


# TODO: Rename this models
class LightingProductNote(models.Model):
    _name = "lighting.product.note"
    _description = "Product Note"
    _order = "name"

    name = fields.Char(
        required=True,
        translate=True,
    )
    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
    )
    product_notes_ids = fields.One2many(
        comodel_name="lighting.product.notes",
        inverse_name="note_id",
        string="Product Notes",
    )

    # TODO: O2m and len
    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec.product_notes_ids)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The note must be unique!"),
    ]
