# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingBMEcatLogisticDetails(models.Model):
    _name = "lighting.bmecat.logistic.details"
    _description = "Lighting BMEcat Logistic Details"

    sequence = fields.Integer(default=1)
    config_id = fields.Many2one(
        comodel_name="lighting.bmecat.config",
        required=True,
        ondelete="cascade",
    )
    dimension = fields.Selection(
        selection=[
            ("net_volume", "Net Volume"),
            ("net_length", "Net Length"),
            ("net_width", "Net Width"),
            ("net_depth", "Net Depth"),
            ("net_diameter", "Net Diameter"),
        ],
        required=True,
    )
    uom_id = fields.Many2one(
        comodel_name="uom.uom", required=True, string="Unit of Measure"
    )
    dimension_type_id = fields.Many2one(
        comodel_name="lighting.dimension.type",
        required=True,
    )
