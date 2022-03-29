# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree

from collections import OrderedDict


class LightingProductSource(models.Model):
    _name = 'lighting.product.source'
    _rec_name = 'relevance'
    _order = 'sequence'

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")

    relevance = fields.Selection([('main', 'Main'), ('aux', 'Auxiliary')], string='Relevance', required=True,
                                 default='main')
    num = fields.Integer(string='Number of sources', default=1)
    lampholder_id = fields.Many2one(comodel_name='lighting.product.source.lampholder', ondelete='restrict',
                                    string='Lampholder')
    lampholder_technical_id = fields.Many2one(comodel_name='lighting.product.source.lampholder', ondelete='restrict',
                                              string='Technical lampholder')

    line_ids = fields.One2many(comodel_name='lighting.product.source.line', inverse_name='source_id', string='Lines',
                               copy=True)

    product_id = fields.Many2one(comodel_name='lighting.product', ondelete='cascade', string='Product')

    ## computed fields
    line_display = fields.Char(compute='_compute_line_display', string='Description')

    @api.depends('line_ids')
    def _compute_line_display(self):
        for rec in self:
            res = []
            for l in rec.line_ids.sorted(lambda x: x.sequence):
                line = [l.type_id.code]

                if l.is_integrated or l.is_lamp_included:
                    if l.color_temperature_flux_ids:
                        if l.color_temperature_display:
                            line.append(l.color_temperature_display)
                        if l.luminous_flux_display:
                            line.append(l.luminous_flux_display)
                    if l.is_led and l.cri_min:
                        line.append("CRI%i" % l.cri_min)
                    if l.is_led and l.leds_m:
                        line.append("%i Leds/m" % l.leds_m)
                    if l.is_led and l.special_spectrum:
                        special_spectrum_values = dict(
                            l.fields_get('special_spectrum', 'selection')['special_spectrum']['selection'])
                        line.append(special_spectrum_values[l.special_spectrum])

                if l.wattage_display:
                    line.append("(%s)" % l.wattage_display)

                res.append(' '.join(line))

            if res != []:
                rec.line_display = " / ".join(res)

    @api.multi
    @api.constrains('lampholder_id', 'lampholder_technical_id')
    def _check_efficiency_lampholder(self):
        for rec in self:
            if all([
                rec.lampholder_id or rec.lampholder_technical_id,
                rec.line_ids.mapped('efficiency_ids'),
                not rec.product_id.is_accessory]
            ):
                raise ValidationError(_("A non accessory source with lampholder cannot have efficiency"))

    ## aux display functions
    def get_source_type(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            s = []
            if src.lampholder_id:
                s.append(src.lampholder_id.display_name)

            src_t = src.line_ids.get_source_type()
            if src_t:
                s.append('/'.join(src_t))

            s_l = None
            if s:
                s_l = ' '.join(s)
            res.append(s_l)

        if not any(res):
            return None
        return res

    def get_color_temperature(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            src_k = src.line_ids.get_color_temperature()
            k_l = None
            if src_k:
                k_l = ','.join(src_k)
            res.append(k_l)

        if not any(res):
            return None
        return res

    def get_luminous_flux(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            src_k = src.line_ids.get_luminous_flux()
            k_l = None
            if src_k:
                kn_l = []
                if src.num > 1:
                    kn_l.append('%ix' % src.num)
                kn_l.append(','.join(src_k))
                k_l = ' '.join(kn_l)
            res.append(k_l)

        if not any(res):
            return None
        return res

    def get_cri(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            src_k = src.line_ids.get_cri()
            if src_k:
                k_l = ','.join(['CRI%i' % x for x in src_k])
                res.append(k_l)

        if not any(res):
            return None
        return res

    def get_leds_m(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            src_k = src.line_ids.get_leds_m()
            if src_k:
                k_l = ','.join([str(x) for x in src_k])
                res.append('%s Leds/m' % (k_l,))

        if not any(res):
            return None
        return res

    def get_special_spectrum(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            src_k = src.line_ids.get_special_spectrum()
            if src_k:
                k_l = ','.join(src_k)
                res.append(k_l)

        if not any(res):
            return None
        return res

    def get_wattage(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            src_k = src.line_ids.get_wattage()
            if src_k:
                kn_l = []
                if src.num > 1:
                    kn_l.append('%ix' % src.num)
                kn_l.append(src_k)
                src_k = ' '.join(kn_l)
            res.append(src_k)

        if not any(res):
            return None
        return res
