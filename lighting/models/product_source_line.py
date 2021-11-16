# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree

from collections import OrderedDict


def float2text(f, decs=2):
    if f == int(f):
        return '%i' % int(f)
    else:
        return ("{0:.%if}" % decs).format(f)


class LightingProductSourceLine(models.Model):
    _name = 'lighting.product.source.line'
    _rec_name = 'type_id'
    _order = 'sequence'

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")

    type_id = fields.Many2one(comodel_name='lighting.product.source.type', ondelete='restrict', string='Type',
                              required=True)

    wattage = fields.Float(string='Wattage')
    is_max_wattage = fields.Boolean(string='Is max. Wattage')
    wattage_magnitude = fields.Selection([('w', 'W'), ('wm', 'W/m')], string='Wattage magnitude', default='w')

    @api.constrains('wattage', 'type_id')
    def _check_wattage(self):
        for rec in self:
            if rec.type_id.is_integrated and rec.wattage <= 0:
                raise ValidationError(
                    "%s: The wattage on line %s must be greater than 0 if source type is integrated" % (
                        rec.source_id.product_id.display_name,
                        rec.type_id.display_name))

    color_temperature_flux_ids = fields.One2many(string='Color temperature/Flux',
                                                 comodel_name='lighting.product.source.line.color.temperature.flux',
                                                 inverse_name='source_line_id',
                                                 copy=True)

    is_color_temperature_flux_tunable = fields.Boolean(string='Tunable', default=False)

    @api.onchange('color_temperature_flux_ids', 'is_color_temperature_flux_tunable')
    def _onchange_is_color_temperature_flux_ids_tunable(self):
        if len(self.color_temperature_flux_ids) > 2:
            if self.is_color_temperature_flux_tunable:
                color_temp_fluxs_ord = self.color_temperature_flux_ids.sorted(lambda x: x.color_temperature_id.value)
                self.color_temperature_flux_ids = [
                    (6, False, (color_temp_fluxs_ord[0] | color_temp_fluxs_ord[-1]).mapped('id'))]
        elif len(self.color_temperature_flux_ids) < 2:
            if self.is_color_temperature_flux_tunable:
                self.is_color_temperature_flux_tunable = False

    color_temperature_display = fields.Char(string='Color temperature',
                                            compute='_compute_color_temperature_flux_display')

    luminous_flux_display = fields.Char(string='Luminous flux',
                                        compute='_compute_color_temperature_flux_display')

    @api.depends('color_temperature_flux_ids',
                 'color_temperature_flux_ids.color_temperature_id',
                 'color_temperature_flux_ids.color_temperature_id.value',
                 'color_temperature_flux_ids.flux_id',
                 'color_temperature_flux_ids.flux_id.value',
                 'color_temperature_flux_ids.flux_magnitude',
                 'is_color_temperature_flux_tunable',
                 'source_id')
    def _compute_color_temperature_flux_display(self):
        for rec in self:
            if rec.color_temperature_flux_ids:
                if len(rec.color_temperature_flux_ids) != 1 or \
                        rec.color_temperature_flux_ids.color_temperature_id.value:
                    color_temperature_values = rec.color_temperature_flux_ids \
                        .filtered(lambda x: not self.env.context.get('ignore_nulls') or x.color_temperature_id.value) \
                        .sorted(lambda x: x.color_temperature_id.value)
                    rec.color_temperature_display = (rec.is_color_temperature_flux_tunable and '-' or '/') \
                        .join([x.color_temperature_id.value and ('%iK' % x.color_temperature_id.value) or '-'
                               for x in color_temperature_values])
                if len(rec.color_temperature_flux_ids) != 1 or \
                        rec.color_temperature_flux_ids.flux_id.value:
                    flux_values = rec.color_temperature_flux_ids \
                        .filtered(lambda x: not self.env.context.get('ignore_nulls') or x.flux_id.value) \
                        .sorted(lambda x: x.color_temperature_id.value)
                    flux_magnitude_options = dict(
                        rec.color_temperature_flux_ids.fields_get(['flux_magnitude'], ['selection'])
                            .get('flux_magnitude').get('selection'))
                    rec.luminous_flux_display = (rec.is_color_temperature_flux_tunable and '-' or '/') \
                        .join([x.flux_id.value and ('%i%s' % (
                        x.flux_id.value, flux_magnitude_options[x.flux_magnitude])) or '-'
                               for x in flux_values])

    ############## to remove
    color_temperature_ids = fields.Many2many(string='Color temperature',
                                             comodel_name='lighting.product.color.temperature',
                                             relation='lighting_product_source_line_color_temperature_rel',
                                             column1='source_line_id', column2='color_temperature_id')
    is_color_temperature_tunable = fields.Boolean(string='Tunableold', default=False)

    luminous_flux1 = fields.Integer(string='Luminous flux 1 (lm)')
    luminous_flux2 = fields.Integer(string='Luminous flux 2 (lm)')

    ###############

    cri_min = fields.Integer(string='CRI', help='Minimum color rendering index', track_visibility='onchange')

    is_led = fields.Boolean(related='type_id.is_led')
    color_consistency = fields.Float(string='Color consistency (SDCM)')
    special_spectrum = fields.Selection(selection=[
        ('meat', 'Meat'), ('fashion', 'Fashion'),
        ('multifood', 'Multi Food'), ('bread', 'Bread'),
        ('fish', 'Fish'), ('vegetable', 'Vegetable'),
        ('blue', _('Blue')), ('orange', _('Orange')),
        ('green', _('Green')), ('red', _('Red')),
        ('purple', _('Purple')), ('pink', _('Pink')),
        ('sunlike', _('Sunlike')), ('dtw', _('DtW')),
        ('tw', _('TW')),
    ], string='Special spectrum')
    leds_m = fields.Integer(string="Leds/m", track_visibility='onchange')
    led_chip_ids = fields.One2many(comodel_name='lighting.product.ledchip',
                                   inverse_name='source_line_id', string='Chip', copy=True)

    efficiency_ids = fields.Many2many(comodel_name='lighting.energyefficiency',
                                      relation='lighting_product_source_energyefficiency_rel',
                                      string='Energy efficiency')

    is_integrated = fields.Boolean(related='type_id.is_integrated')
    is_lamp_included = fields.Boolean(string='Lamp included?')
    lamp_included_efficiency_ids = fields.Many2many(comodel_name='lighting.energyefficiency',
                                                    relation='lighting_product_source_lampenergyefficiency_rel',
                                                    string='Lamp included efficiency')

    ## computed fields
    wattage_display = fields.Char(compute='_compute_wattage_display', string='Wattage (W)')

    def prepare_wattage_str(self, mult=1, is_max_wattage=None):
        self.ensure_one()

        if is_max_wattage is None:
            is_max_wattage = self.is_max_wattage

        wattage_magnitude_option = dict(
            self.fields_get(['wattage_magnitude'], ['selection']).get('wattage_magnitude').get('selection'))

        res = []
        if self.wattage > 0:
            wattage_str = float2text(self.wattage)
            if mult > 1:
                wattage_str = '%ix%s' % (mult, wattage_str)

            if self.wattage_magnitude:
                wattage_str += wattage_magnitude_option.get(self.wattage_magnitude)
            res.append(wattage_str)

        if is_max_wattage:
            res.append(_('max.'))

        if res != []:
            return " ".join(res)
        else:
            return False

    @api.depends('wattage', 'is_max_wattage', 'wattage_magnitude')
    def _compute_wattage_display(self):
        for rec in self:
            rec.wattage_display = rec.prepare_wattage_str()

    source_id = fields.Many2one(comodel_name='lighting.product.source', ondelete='cascade', string='Source')

    @api.multi
    @api.constrains('type_id')
    def _check_integrated_vs_lamp_included(self):
        for rec in self:
            if rec.type_id.is_integrated:
                rec.is_lamp_included = False

    @api.multi
    @api.constrains('color_temperature_flux_ids', 'is_color_temperature_flux_tunable')
    def _check_color_temperature_flux_ids_tunable(self):
        if self.is_color_temperature_flux_tunable and self.color_temperature_flux_ids and \
                len(self.color_temperature_flux_ids) != 2:
            raise ValidationError(_("A tunable source must have exactly 2 pairs color temperature/luminous flux"))

    # aux display fucnitons
    def get_source_type(self):
        res = self.sorted(lambda x: x.sequence) \
            .mapped('type_id.display_name')
        if not res:
            return None
        return res

    def get_color_temperature(self):
        res = self.filtered(lambda x: x.color_temperature_flux_ids) \
            .filtered(lambda x: x.color_temperature_display) \
            .sorted(lambda x: x.sequence) \
            .mapped('color_temperature_display')
        if not res:
            return None
        return res

    def get_luminous_flux(self):
        res = self.filtered(lambda x: x.color_temperature_flux_ids) \
            .filtered(lambda x: x.luminous_flux_display) \
            .sorted(lambda x: x.sequence) \
            .mapped('luminous_flux_display')
        if not res:
            return None
        return res

    def get_special_spectrum(self):
        special_spectrum_option = dict(
            self.fields_get(['special_spectrum'], ['selection'])
                .get('special_spectrum').get('selection'))
        res = [special_spectrum_option[x] for x in self.filtered(lambda x: x.special_spectrum) \
            .sorted(lambda x: x.sequence) \
            .mapped('special_spectrum')]
        if not res:
            return None
        return res

    def get_cri(self):
        res = self.sorted(lambda x: x.sequence) \
            .filtered(lambda x: x.cri_min) \
            .mapped('cri_min')
        if not res:
            return None
        return res

    def get_leds_m(self):
        res = self.sorted(lambda x: x.sequence) \
            .filtered(lambda x: x.leds_m) \
            .mapped('leds_m')
        if not res:
            return None
        return res

    def get_wattage(self):
        w_d = {}
        for rec in self:
            if rec.wattage:
                if rec.wattage_magnitude not in w_d:
                    w_d[rec.wattage_magnitude] = []
                w_d[rec.wattage_magnitude].append(rec.wattage)

        if not w_d:
            return None

        wattage_magnitude_option = dict(
            self.fields_get(['wattage_magnitude'], ['selection'])
                .get('wattage_magnitude').get('selection'))

        w_l = []
        for wm, wv_l in w_d.items():
            ws = wattage_magnitude_option.get(wm)
            w_l.append('%g%s' % (max(wv_l), ws))

        return '%s %s' % ('/'.join(w_l), _('max.'))
