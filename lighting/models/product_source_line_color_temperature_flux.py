# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductSourceLineColorTemperatureFlux(models.Model):
    _name = 'lighting.product.source.line.color.temperature.flux'
    _order = 'color_temperature_value'

    color_temperature_id = fields.Many2one(string='Color temperature',
                                           comodel_name='lighting.product.color.temperature',
                                           required=True,
                                           ondelete='restrict')
    color_temperature_value = fields.Integer(
        compute='_compute_color_temperature_value',
        store=True
    )

    @api.depends('color_temperature_id.value')
    def _compute_color_temperature_value(self):
        for record in self:
            record.color_temperature_value = record.color_temperature_id.value

    nominal_flux = fields.Float(string='Nominal flux',
                                required=True)
    total_flux = fields.Float(string='Total flux',
                              help='Luminaire total nominal flux')
    flux_magnitude = fields.Selection(
        string='Flux Magnitude',
        selection=[('lm', 'lm'), ('lmm', 'lm/m')],
        required=True,
        default='lm')

    source_line_id = fields.Many2one(comodel_name='lighting.product.source.line',
                                     required=True,
                                     ondelete='cascade')
    efficiency_id = fields.Many2one(comodel_name='lighting.energyefficiency',
                                    string='Energy efficiency', )

    _sql_constraints = [('k_uniq', 'unique (source_line_id, color_temperature_id)',
                         'The color temperature must be unique per source line'),
                        ]

    @api.multi
    @api.constrains('efficiency_id', 'source_line_id')
    def _check_efficiency(self):
        for rec in self:
            if rec.efficiency_id and rec.source_line_id.efficiency_ids:
                raise ValidationError(_("Efficiency must be defined only in CCT table"))
