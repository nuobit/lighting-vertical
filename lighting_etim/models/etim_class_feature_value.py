# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions 2025 - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingETIMClassFeatureValue(models.Model):
    _name = "lighting.etim.class.feature.value"
    _description = "ETIM Class Feature Value"
    _order = "sequence"

    sequence = fields.Integer(
        string="Order",
        required=True,
        default=1,
    )

    change_code = fields.Char(
        required=True,
    )

    value_id = fields.Many2one(
        comodel_name="lighting.etim.value",
        ondelete="restrict",
    )

    feature_id = fields.Many2one(
        comodel_name="lighting.etim.class.feature",
        ondelete="cascade",
    )
