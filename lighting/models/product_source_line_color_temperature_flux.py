# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LightingProductSourceLineColorTemperatureFlux(models.Model):
    _name = "lighting.product.source.line.color.temperature.flux"
    _description = "Product Source Line Color Temperature Flux"
    _order = "color_temperature_value"

    color_temperature_id = fields.Many2one(
        comodel_name="lighting.product.color.temperature",
        required=True,
        ondelete="restrict",
    )
    color_temperature_value = fields.Integer(
        compute="_compute_color_temperature_value",
        store=True,
    )

    @api.depends("color_temperature_id.value")
    def _compute_color_temperature_value(self):
        for record in self:
            record.color_temperature_value = record.color_temperature_id.value

    nominal_flux = fields.Float(
        required=True,
    )
    total_flux = fields.Float(
        help="Luminaire total nominal flux",
    )
    flux_magnitude = fields.Selection(
        selection=[("lm", "lm"), ("lmm", "lm/m")],
        required=True,
        default="lm",
    )
    source_line_id = fields.Many2one(
        comodel_name="lighting.product.source.line",
        required=True,
        ondelete="cascade",
    )
    efficiency_id = fields.Many2one(
        comodel_name="lighting.energyefficiency",
        string="Energy efficiency",
    )

    _sql_constraints = [
        (
            "k_uniq",
            "unique (source_line_id, color_temperature_id)",
            "The color temperature must be unique per source line",
        ),
    ]

    @api.constrains("efficiency_id", "source_line_id")
    def _check_efficiency(self):
        for rec in self:
            if rec.efficiency_id and rec.source_line_id.efficiency_ids:
                raise ValidationError(_("Efficiency must be defined only in CCT table"))
