# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingETIMClassFeature(models.Model):
    _name = "lighting.etim.class.feature"
    _order = "sequence"

    sequence = fields.Integer(
        string="Order",
        required=True,
        default=1,
    )
    change_code = fields.Char(
        required=True,
    )
    feature_id = fields.Many2one(
        comodel_name="lighting.etim.feature",
        ondelete="restrict",
    )
    unit_id = fields.Many2one(
        comodel_name="lighting.etim.unit",
        ondelete="restrict",
    )

    value_ids = fields.One2many(
        comodel_name="lighting.etim.class.feature.value",
        inverse_name="feature_id",
        string="Values",
    )

    class_id = fields.Many2one(
        comodel_name="lighting.etim.class",
        ondelete="cascade",
    )
