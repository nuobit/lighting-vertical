# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
import re
from collections import OrderedDict

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

YESNO = [
    ('Y', _('Yes')),
    ('N', _('No')),
]

STATES_MARKETING = [
    ('O', 'Online'),
    ('N', 'New'),
    ('C', 'Cataloged'),
    ('ES', 'Until end of stock'),
    ('ESH', 'Until end of stock (historical)'),
    ('D', 'Discontinued'),
    ('H', 'Historical'),
]

ES_MAP = {'ES': 'D', 'ESH': 'H'}
D_MAP = {v: k for k, v in ES_MAP.items()}
C_STATES = {'O', 'N', 'C', False}
STATE_NAME_MAP = lambda x: {
    False: '',
    **dict(x.fields_get('state_marketing', 'selection')['state_marketing']['selection'])
}


class LightingProduct(models.Model):
    _name = 'lighting.product'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {"product.product": "odoop_id"}
    _rec_name = 'reference'
    _order = 'sequence,reference'
    _description = 'Product'

    # binding fields
    odoop_id = fields.Many2one(
        comodel_name="product.product",
        string="Odoo Product ID",
        required=True,
        ondelete="cascade",
    )

    # Common data
    reference = fields.Char(string='Reference', required=True, track_visibility='onchange')

    # image: all image fields are base64 encoded and PIL-supported
    image_small = fields.Binary("Small-sized image", attachment=True, compute='_compute_images', store=True)
    image_medium = fields.Binary("Medium-sized image", attachment=True, compute='_compute_images', store=True)

    @api.depends('attachment_ids.datas_location', 'attachment_ids.datas', 'attachment_ids.datas_url',
                 'attachment_ids.image_small', 'attachment_ids.image_medium',
                 'attachment_ids.sequence',
                 'attachment_ids.type_id', 'attachment_ids.type_id.is_image')
    def _compute_images(self):
        for rec in self:
            resized_images = rec.attachment_ids.get_main_resized_image()
            if resized_images:
                rec.image_medium = resized_images['image_medium']
                rec.image_small = resized_images['image_small']

    description_updated = fields.Boolean(default=False)
    description = fields.Char(compute='_compute_description', string='Description', readonly=True,
                              help="Description dynamically generated from product data",
                              translate=True, store=True, track_visibility='onchange')

    @api.depends('category_id.name',
                 'category_id.description_text',
                 'category_id.effective_description_dimension_ids',
                 'model_id',
                 'model_id.name',
                 'family_ids.name',
                 'catalog_ids.description_show_ip',
                 'catalog_ids.description_show_ip_condition',
                 'sealing_id',
                 'sealing_id.name',
                 'diffusor_material_ids',
                 'diffusor_material_ids.name',
                 'diffusor_material_ids.is_glass',
                 'sensor_ids',
                 'sensor_ids.name',
                 'dimmable_ids.name',
                 'dimension_ids',
                 'dimension_ids.type_id',
                 'dimension_ids.type_id.code',
                 'dimension_ids.value',
                 'source_ids.sequence',
                 'source_ids.lampholder_id.code',
                 'source_ids.line_ids.sequence',
                 'source_ids.line_ids.type_id.code',
                 'source_ids.line_ids.type_id.is_integrated',
                 'source_ids.line_ids.type_id.is_led',
                 'source_ids.line_ids.type_id.description_text',
                 'source_ids.line_ids.is_lamp_included',
                 'source_ids.line_ids.wattage',
                 'source_ids.line_ids.wattage_magnitude',
                 'source_ids.line_ids.cri_min',
                 'source_ids.line_ids.special_spectrum',
                 'source_ids.line_ids.is_color_temperature_flux_tunable',
                 'source_ids.line_ids.color_temperature_flux_ids',
                 'source_ids.line_ids.color_temperature_flux_ids.color_temperature_id',
                 'source_ids.line_ids.color_temperature_flux_ids.color_temperature_id.value',
                 'source_ids.line_ids.color_temperature_flux_ids.nominal_flux',
                 'beam_ids.dimension_ids',
                 'beam_ids.dimension_ids.type_id',
                 'beam_ids.dimension_ids.type_id.code',
                 'beam_ids.dimension_ids.type_id.uom',
                 'beam_ids.dimension_ids.value',
                 'finish_id.name',
                 'finish2_id.name',
                 'inclination_angle_max')
    def _compute_description(self):
        for rec in self:
            rec.description_updated = True
            rec.description = rec._generate_description()

    @api.multi
    def _update_computed_descriptions(self, exclude_lang=[]):
        exclude_lang = list(map(lambda x: x or 'en_US', exclude_lang))
        for rec in self:
            self.env.cr.execute('select description from lighting_product where id=%s', (rec.id,))
            en_trl = self.env.cr.fetchone()[0]
            if 'en_US' not in exclude_lang:
                en_trl1 = rec.with_context(lang=None)._generate_description()
                if en_trl1 != en_trl:
                    en_trl = en_trl1
                    self.env.cr.execute('update lighting_product set description=%s where id=%s', (en_trl, rec.id,))
            for lang in self.env['res.lang'].search([('code', 'not in', exclude_lang + ['en_US'])]):
                non_en_trl = rec.with_context(lang=lang.code)._generate_description()
                values = {
                    'state': 'translated',
                    'value': non_en_trl,
                }
                trl = self.env['ir.translation'].search([
                    ('name', '=', 'lighting.product,description'),
                    ('lang', '=', lang.code),
                    ('res_id', '=', rec.id),
                ])
                if not trl:
                    values.update({
                        'name': 'lighting.product,description',
                        'type': 'model',
                        'lang': lang.code,
                        'res_id': rec.id,
                        'src': en_trl,
                    })
                    self.env['ir.translation'].create(values)
                else:
                    if trl.state != 'translated' or trl.src != en_trl or trl.value != non_en_trl:
                        if 'en_US' not in exclude_lang:
                            values.update({
                                'src': en_trl,
                            })
                        trl.with_context(lang=None).write(values)

    def _generate_description(self, show_variant_data=True):
        self.ensure_one()
        _logger.info(_("Generating %s description for %s") % (self.env.lang or 'en_US', self.reference))
        data = []
        if self.category_id:
            data.append(self.category_id.description_text or self.category_id.name)

        if self.inclination_angle_max:
            data.append("tilt")

        if self.family_ids:
            data.append(','.join(map(lambda x: x.upper(),
                                     self.family_ids.sorted(lambda x: (x.sequence, x.name)).mapped('name'))))
        if self.model_id:
            data.append(self.model_id.name)

        if self.sealing_id:
            sealing_id = self.sealing_id
            for catalog in self.catalog_ids:
                if catalog.description_show_ip:
                    if self.sealing_id:
                        break
                else:
                    ip_condition = catalog.description_show_ip_condition and \
                                   catalog.description_show_ip_condition.strip() or None
                    if ip_condition:
                        try:
                            expr = ip_condition % dict(value="'%s'" % self.sealing_id.name)
                            if safe_eval(expr):
                                break
                        except ValueError as e:
                            raise UserError(_("Incorrect format expression: %s") % expr)
            else:
                sealing_id = None
            if sealing_id:
                data.append(sealing_id.name)

        if self.dimmable_ids:
            data.append(','.join(self.dimmable_ids.sorted(lambda x: x.name).mapped('name')))

        data_sources = []
        for source in self.source_ids.sorted(lambda x: x.sequence):
            data_source = []
            if source.lampholder_id:
                data_source.append(source.lampholder_id.code)

            type_d = OrderedDict()
            for line in source.line_ids.sorted(lambda x: (x.type_id.is_integrated, x.sequence)):
                is_integrated = line.type_id.is_integrated
                if is_integrated not in type_d:
                    type_d[is_integrated] = []
                type_d[is_integrated].append(line)

            data_lines = []
            for is_integrated, lines in type_d.items():
                if is_integrated:
                    for line in lines:
                        data_line = []
                        data_line.append(line.type_id.description_text or line.type_id.code)

                        wattage_total_display = line.prepare_wattage_str(mult=line.source_id.num or 1,
                                                                         is_max_wattage=False)
                        if wattage_total_display:
                            data_line.append(wattage_total_display)

                        if line.color_temperature_flux_ids:
                            luminous_flux_display = line.with_context(ignore_nulls=True).luminous_flux_display
                            if luminous_flux_display:
                                data_line.append(luminous_flux_display)

                        if line.cri_min:
                            data_line.append("CRI%i" % line.cri_min)

                        if line.color_temperature_flux_ids:
                            color_temperature_display = line.with_context(ignore_nulls=True).color_temperature_display
                            if color_temperature_display:
                                data_line.append(color_temperature_display)

                        if not line.color_temperature_flux_ids:
                            if line.is_led and line.special_spectrum:
                                special_spectrum_option = dict(
                                    line.fields_get(['special_spectrum'], ['selection']) \
                                        .get('special_spectrum').get('selection'))
                                data_line.append(special_spectrum_option.get(line.special_spectrum))

                        if data_line:
                            data_lines.append(' '.join(data_line))
                else:
                    lamp_d = OrderedDict()
                    for line in lines:
                        is_lamp_included = line.is_lamp_included
                        if is_lamp_included not in lamp_d:
                            lamp_d[is_lamp_included] = []
                        lamp_d[is_lamp_included].append(line)

                    data_lines = []
                    for is_lamp_included, llines in lamp_d.items():
                        if is_lamp_included:
                            for line in llines:
                                data_line = []
                                data_line.append(line.type_id.description_text or line.type_id.code)

                                wattage_total_display = line.prepare_wattage_str(mult=line.source_id.num or 1,
                                                                                 is_max_wattage=False)
                                if wattage_total_display:
                                    data_line.append(wattage_total_display)

                                if line.color_temperature_flux_ids:
                                    if line.luminous_flux_display:
                                        data_line.append(line.luminous_flux_display)

                                if line.cri_min:
                                    data_line.append("CRI%i" % line.cri_min)

                                if line.color_temperature_flux_ids:
                                    if line.color_temperature_display:
                                        data_line.append(line.color_temperature_display)

                                if not line.color_temperature_flux_ids:
                                    if line.is_led and line.special_spectrum:
                                        special_spectrum_option = dict(
                                            line.fields_get(['special_spectrum'], ['selection']) \
                                                .get('special_spectrum').get('selection'))
                                        data_line.append(special_spectrum_option.get(line.special_spectrum))

                                if data_line:
                                    data_lines.append(' '.join(data_line))
                        else:
                            wattage_d = {}
                            for line in llines:
                                if line.wattage > 0 and line.wattage_magnitude:
                                    if line.wattage_magnitude not in wattage_d:
                                        wattage_d[line.wattage_magnitude] = []
                                    wattage_d[line.wattage_magnitude].append(line)

                            for wlines in wattage_d.values():
                                line_max = sorted(wlines, key=lambda x: x.wattage, reverse=True)[0]
                                wattage_total_display = line_max.prepare_wattage_str(mult=line_max.source_id.num or 1,
                                                                                     is_max_wattage=False)
                                if wattage_total_display:
                                    data_lines.append(wattage_total_display)

            if data_lines:
                data_source.append(','.join(data_lines))

            if data_source:
                data_sources.append(' '.join(data_source))

        if data_sources:
            data.append('+'.join(data_sources))

        if self.beam_ids:
            beam_angle_display = self.beam_ids.get_beam_angle_display()
            if beam_angle_display:
                data.append(beam_angle_display)

        if self.sensor_ids:
            data.append(','.join(self.sensor_ids.sorted(lambda x: x.name).mapped('name')))

        if self.charger_connector_type_id:
            data.append(self.charger_connector_type_id.name)

        if self.category_id:
            if self.category_id.effective_description_dimension_ids:
                if self.dimension_ids:
                    dimensions = self.dimension_ids.filtered(
                        lambda x: x.type_id in self.category_id.effective_description_dimension_ids)
                    if dimensions:
                        data.append(dimensions.get_value_display(spaces=False))

        if self.family_ids:
            if set(self.family_ids.mapped('code')) & {'984', 'GLOB', '129', '393'}:
                diameter_dimension = self.dimension_ids.filtered(lambda x: x.type_id.code == 'DIAMETERMM')
                if diameter_dimension:
                    data.append('\u2300%s' % diameter_dimension.get_value_display(spaces=False))

        if self.family_ids:
            if set(self.family_ids.mapped('code')) & {'984', '264', '096'}:
                glass_diffuser_material = self.diffusor_material_ids.filtered(lambda x: x.is_glass)
                if glass_diffuser_material:
                    data.append(','.join(glass_diffuser_material.mapped('name')))

        if self.beam_count == 2:
            data.append("up-down")

        if show_variant_data and self.finish_id:
            data.append(self.finish_id.name)

        if self.finish2_id:
            data.append(self.finish2_id.name)

        if data:
            return ' '.join(data)
        else:
            return None

    description_manual = fields.Char(string='Description (manual)', help='Manual description', translate=True,
                                     track_visibility='onchange')

    ean = fields.Char(string='EAN', required=False, readonly=True, track_visibility='onchange')

    product_group_id = fields.Many2one(comodel_name='lighting.product.group',
                                       string='Group',
                                       ondelete='restrict', track_visibility='onchange')

    family_ids = fields.Many2many(comodel_name='lighting.product.family',
                                  relation='lighting_product_family_rel', string='Families',
                                  required=False,
                                  track_visibility='onchange')
    catalog_ids = fields.Many2many(comodel_name='lighting.catalog', relation='lighting_product_catalog_rel',
                                   string='Catalogs', required=True, track_visibility='onchange')

    category_id = fields.Many2one(comodel_name='lighting.product.category',
                                  string='Category', required=False,
                                  ondelete='restrict', track_visibility='onchange')

    category_completename = fields.Char(string='Category (complete name)',
                                        compute='_compute_category_complete_name',
                                        inverse='_inverse_category_complete_name')

    def _compute_category_complete_name(self):
        for rec in self:
            rec.category_completename = rec.category_id and rec.category_id.complete_name or False

    def _inverse_category_complete_name(self):
        for rec in self:
            if rec.category_completename:
                category_leafs = self.env['lighting.product.category']. \
                    get_leaf_from_complete_name(rec.category_completename)
                if category_leafs:
                    rec.category_id = category_leafs[0]
                else:
                    raise ValidationError(
                        _("Category with complete name '%s' does not exist") % rec.category_completename)
            else:
                rec.category_id = False

    model_id = fields.Many2one(
        string="Model",
        comodel_name='lighting.product.model',
    )
    is_accessory = fields.Boolean(
        string="Is accessory",
        compute="_compute_is_accessory",
        search="_search_is_accessory",
        readonly=True)

    @api.depends('category_id', 'category_id.is_accessory')
    def _compute_is_accessory(self):
        for rec in self:
            if rec.category_id:
                rec.is_accessory = rec.category_id._get_is_accessory()

    def _search_is_accessory(self, operator, value):
        ids = []
        for prod in self.env['lighting.product'].search([
            ('category_id', '!=', False),
        ]):
            is_accessory = prod.category_id._get_is_accessory()
            if operator == '=':
                if is_accessory == value:
                    ids.append(prod.id)
            elif operator == '!=':
                if is_accessory != value:
                    ids.append(prod.id)
            else:
                raise ValidationError("Operator '%s' not supported" % operator)
        return [('id', 'in', ids)]

    is_composite = fields.Boolean(string="Is composite", default=False)

    @api.onchange('is_composite')
    def _onchange_is_composite(self):
        if not self.is_composite and self.required_ids:
            self.is_composite = True
            return {
                'warning': {'title': "Warning",
                            'message': _(
                                "You cannot change this while the product has necessary accessories assigned")},
            }

    parents_brand_ids = fields.Many2many(comodel_name='lighting.catalog',
                                         compute='_compute_parents_brands',
                                         readonly=True,
                                         string='Parents brands',
                                         help='Brands of the products that one of their optional and/or '
                                              'required accessories is the current product')

    @api.depends('optional_ids', 'required_ids')
    def _compute_parents_brands(self):
        for rec in self:
            parents = self.env['lighting.product'].search([
                '|',
                ('optional_ids', '=', rec.id),
                ('required_ids', '=', rec.id),
            ])
            if parents:
                brand_ids = list(set(parents.mapped('catalog_ids.id')))
                rec.parents_brand_ids = [(6, False, brand_ids)]

    last_update = fields.Date(string='Last modified on', track_visibility='onchange')

    configurator = fields.Boolean(string="Configurator", required=True, default=False,
                                  track_visibility='onchange')

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order",
                              track_visibility='onchange')

    _sql_constraints = [('reference_uniq', 'unique (reference)', 'The reference must be unique!'),
                        ('ean_uniq', 'unique (ean)', 'The EAN must be unique!')
                        ]

    # Description tab
    location_ids = fields.Many2many(comodel_name='lighting.product.location',
                                    relation='lighting_product_location_rel', string='Locations',
                                    required=False,
                                    track_visibility='onchange')

    installation_ids = fields.Many2many(comodel_name='lighting.product.installation',
                                        relation='lighting_product_installation_rel', string='Installations',
                                        track_visibility='onchange')

    application_ids = fields.Many2many(comodel_name='lighting.product.application',
                                       relation='lighting_product_application_rel', string='Applications',
                                       track_visibility='onchange')
    finish_id = fields.Many2one(comodel_name='lighting.product.finish', ondelete='restrict', string='Finish',
                                track_visibility='onchange')

    finish_prefix = fields.Char(string='Finish prefix', compute='_compute_finish_prefix')

    def _compute_finish_prefix(self):
        for rec in self:
            has_sibling = False
            m = re.match(r'^(.+)-.{2}$', rec.reference)
            if m:
                prefix = m.group(1)
                product_siblings = self.search([
                    ('reference', '=like', '%s-__' % prefix),
                    ('id', '!=', rec.id),
                ])
                for p in product_siblings:
                    rec.finish_prefix = prefix
                    has_sibling = True
                    break

            if not has_sibling:
                rec.finish_prefix = rec.reference

    finish2_id = fields.Many2one(comodel_name='lighting.product.finish', ondelete='restrict', string='Finish 2',
                                 track_visibility='onchange')

    ral_id = fields.Many2one(comodel_name='lighting.product.ral', ondelete='restrict', string='RAL',
                             track_visibility='onchange')

    body_material_ids = fields.Many2many(comodel_name='lighting.product.material',
                                         relation='lighting_product_body_material_rel',
                                         string='Body material', track_visibility='onchange')
    lampshade_material_ids = fields.Many2many(comodel_name='lighting.product.material',
                                              relation='lighting_product_lampshade_material_rel',
                                              string='Lampshade material', track_visibility='onchange')
    diffusor_material_ids = fields.Many2many(comodel_name='lighting.product.material',
                                             relation='lighting_product_diffusor_material_rel',
                                             string='Diffuser material', track_visibility='onchange')
    frame_material_ids = fields.Many2many(comodel_name='lighting.product.material',
                                          relation='lighting_product_frame_material_rel',
                                          string='Frame material', track_visibility='onchange')
    reflector_material_ids = fields.Many2many(comodel_name='lighting.product.material',
                                              relation='lighting_product_reflector_material_rel',
                                              string='Reflector material', track_visibility='onchange')
    blade_material_ids = fields.Many2many(comodel_name='lighting.product.material',
                                          relation='lighting_product_blade_material_rel',
                                          string='Blade material', track_visibility='onchange')

    sealing_id = fields.Many2one(comodel_name='lighting.product.sealing',
                                 ondelete='restrict',
                                 string='Sealing', track_visibility='onchange')
    sealing2_id = fields.Many2one(comodel_name='lighting.product.sealing',
                                  ondelete='restrict',
                                  string='Sealing 2', track_visibility='onchange')

    ik = fields.Selection(selection=[("%02d" % x, "%02d" % x) for x in range(11)],
                          string='IK', track_visibility='onchange')

    static_pressure = fields.Float(string="Static pressure (kg)", track_visibility='onchange')
    dynamic_pressure = fields.Float(string="Dynamic pressure (kg)", track_visibility='onchange')
    dynamic_pressure_velocity = fields.Float(string="Dynamic pressure (km/h)", track_visibility='onchange')
    corrosion_resistance = fields.Selection(selection=YESNO, string="Corrosion resistance", track_visibility='onchange')
    technical_comments = fields.Char(string='Technical comments', track_visibility='onchange')

    # electrical characteristics tab
    protection_class_id = fields.Many2one(comodel_name='lighting.product.protectionclass',
                                          ondelete='restrict',
                                          string='Protection class', track_visibility='onchange')
    frequency_id = fields.Many2one(comodel_name='lighting.product.frequency',
                                   ondelete='restrict', string='Frequency (Hz)', track_visibility='onchange')
    dimmable_ids = fields.Many2many(comodel_name='lighting.product.dimmable',
                                    relation='lighting_product_dimmable_rel',
                                    string='Dimmables', track_visibility='onchange')
    auxiliary_equipment_ids = fields.Many2many(comodel_name='lighting.product.auxiliaryequipment',
                                               relation='lighting_product_auxiliary_equipment_rel',
                                               string='Auxiliary gear', track_visibility='onchange')
    auxiliary_equipment_model_ids = fields.One2many(comodel_name='lighting.product.auxiliaryequipmentmodel',
                                                    inverse_name='product_id',
                                                    string='Auxiliary gear code', copy=True,
                                                    track_visibility='onchange')
    auxiliary_equipment_model_alt = fields.Char(string='Alternative auxiliary gear code', track_visibility='onchange')
    input_voltage_id = fields.Many2one(comodel_name='lighting.product.voltage',
                                       ondelete='restrict', string='Input voltage', track_visibility='onchange')
    input_current = fields.Integer(string='Input current (mA)', track_visibility='onchange')
    output_voltage_id = fields.Many2one(comodel_name='lighting.product.voltage',
                                        ondelete='restrict', string='Output voltage', track_visibility='onchange')
    output_current = fields.Integer(string='Output current (mA)', track_visibility='onchange')

    total_wattage = fields.Float(compute='_compute_total_wattage',
                                 inverse='_inverse_total_wattage',
                                 string='Total wattage (W)', help='Total power consumed by the luminaire',
                                 store=True, track_visibility='onchange')
    total_wattage_auto = fields.Boolean(string='Autocalculate',
                                        help='Autocalculate total wattage', default=True, track_visibility='onchange')

    @api.depends('total_wattage_auto', 'source_ids.line_ids.wattage', 'source_ids.line_ids.type_id',
                 'source_ids.line_ids.type_id.is_integrated',
                 'source_ids.line_ids.is_lamp_included')
    def _compute_total_wattage(self):
        for rec in self:
            if rec.total_wattage_auto:
                rec.total_wattage = 0
                line_l = rec.source_ids.mapped('line_ids').filtered(lambda x: x.is_integrated or x.is_lamp_included)
                for line in line_l:
                    if line.wattage <= 0:
                        raise ValidationError("%s: The source line %s has invalid wattage" % (rec.display_name,
                                                                                              line.type_id.display_name))
                    rec.total_wattage += line.source_id.num * line.wattage

    def _inverse_total_wattage(self):
        ## dummy method. It allows to update calculated field
        pass

    power_factor_min = fields.Float(string='Minimum power factor', track_visibility='onchange')
    power_switches = fields.Integer(string='Power switches', help="Number of power switches",
                                    track_visibility='onchange')

    usb_ports = fields.Integer(string='USB ports charging devices', help="Number of USB charging ports",
                               track_visibility='onchange')
    usb_voltage = fields.Float(string='USB charging voltage (V)', track_visibility='onchange')
    usb_current = fields.Float(string='USB charging current (mA)', track_visibility='onchange')

    charger_connector_type_id = fields.Many2one(comodel_name='lighting.product.connectortype',
                                                ondelete='restrict',
                                                string='Charger connector type', track_visibility='onchange')

    sensor_ids = fields.Many2many(comodel_name='lighting.product.sensor', relation='lighting_product_sensor_rel',
                                  string='Sensors', track_visibility='onchange')

    rechargeable_type = fields.Selection(
        selection=[('solar', 'Solar'), ('charger', 'With charger'), ('solarcharger', 'Solar/With charger')],
        string='Rechargeable', track_visibility='onchange',
    )
    battery_autonomy = fields.Float(string='Battery autonomy (h)', track_visibility='onchange')
    battery_charge_time = fields.Float(string='Battery charge time (h)', track_visibility='onchange')
    battery_charge_capacity = fields.Integer(string='Battery charge capacity (mAH)', track_visibility='onchange')
    battery_output_voltage = fields.Float(string='Battery output voltage (V)', digits=(5, 1),
                                          track_visibility='onchange')
    surface_temperature = fields.Float(string='Surface temperature (ºC)', track_visibility='onchange')
    operating_temperature_min = fields.Float(string='Minimum operating temperature (ºC)', track_visibility='onchange')
    operating_temperature_max = fields.Float(string='Maximum operating temperature (ºC)', track_visibility='onchange')

    glow_wire_temperature = fields.Float(string='Glow wire temperature (ºC)', track_visibility='onchange')

    # light characteristics tab
    total_nominal_flux = fields.Float(string='Total flux (lm)', help='Luminaire total nominal flux',
                                      track_visibility='onchange')
    ugr_max = fields.Integer(string='UGR', help='Maximum unified glare rating', track_visibility='onchange')

    lifetime = fields.Integer(string='Lifetime (h)', track_visibility='onchange')

    led_lifetime_l = fields.Integer(string='LED lifetime L', track_visibility='onchange')
    led_lifetime_b = fields.Integer(string='LED lifetime B', track_visibility='onchange')

    # Physical characteristics
    weight = fields.Float(string='Weight (kg)', track_visibility='onchange')
    dimension_ids = fields.One2many(comodel_name='lighting.product.dimension',
                                    inverse_name='product_id', string='Dimensions', copy=True,
                                    track_visibility='onchange')

    cutting_length = fields.Float(string='Cutting length (mm)', track_visibility='onchange')
    cable_outlets = fields.Integer(string='Cable outlets', help="Number of cable outlets", track_visibility='onchange')
    lead_wire_length = fields.Float(string='Length of the lead wire supplied (mm)', track_visibility='onchange')
    inclination_angle_max = fields.Float(string='Maximum tilt angle (º)', track_visibility='onchange')
    rotation_angle_max = fields.Float(string='Maximum rotation angle (º)', track_visibility='onchange')
    recessing_box_included = fields.Selection(selection=YESNO, string='Cut hole box included',
                                              track_visibility='onchange')
    recess_dimension_ids = fields.One2many(comodel_name='lighting.product.recessdimension',
                                           inverse_name='product_id', string='Cut hole dimensions',
                                           copy=True, track_visibility='onchange')
    ecorrae_category_id = fields.Many2one(comodel_name='lighting.product.ecorraecategory', ondelete='restrict',
                                          string='ECORRAE I category', track_visibility='onchange')
    ecorrae2_category_id = fields.Many2one(comodel_name='lighting.product.ecorraecategory', ondelete='restrict',
                                           string='ECORRAE II category', track_visibility='onchange')
    ecorrae = fields.Float(string='ECORRAE I', track_visibility='onchange')
    ecorrae2 = fields.Float(string='ECORRAE II', track_visibility='onchange')

    periodic_maintenance = fields.Selection(selection=YESNO, string='Periodic maintenance', track_visibility='onchange')
    anchorage_included = fields.Selection(selection=YESNO, string='Anchorage included', track_visibility='onchange')
    post_included = fields.Selection(selection=YESNO, string='Post included', track_visibility='onchange')
    post_with_inspection_chamber = fields.Selection(selection=YESNO, string='Post with inspection chamber',
                                                    track_visibility='onchange')

    emergency_light = fields.Selection(selection=YESNO, string='Emergency light', help="Luminarie with emergency light",
                                       track_visibility='onchange')
    average_emergency_time = fields.Float(string='Average emergency time (h)', track_visibility='onchange')

    flammable_surfaces = fields.Selection(selection=YESNO, string='Flammable surfaces', track_visibility='onchange')

    photobiological_risk_group_id = fields.Many2one(comodel_name='lighting.product.photobiologicalriskgroup',
                                                    ondelete='restrict',
                                                    string='Photobiological risk group', track_visibility='onchange')

    mechanical_screwdriver = fields.Selection(selection=YESNO, string='Electric screwdriver',
                                              track_visibility='onchange')

    fan_blades = fields.Integer(string='Fan blades', help='Number of fan blades', track_visibility='onchange')
    fan_control = fields.Selection(selection=[('remote', 'Remote control'), ('wall', 'Wall control')],
                                   string='Fan control type', track_visibility='onchange')
    fan_wattage_ids = fields.One2many(comodel_name='lighting.product.fanwattage',
                                      inverse_name='product_id', string='Fan wattages (W)', copy=True,
                                      track_visibility='onchange')

    fan_noise_level = fields.Float(string='Noise level (dB)', track_visibility='onchange')
    fan_reverse_direction = fields.Selection(selection=YESNO, string='Reverse direction', track_visibility='onchange')

    # Sources tab
    source_ids = fields.One2many(comodel_name='lighting.product.source',
                                 inverse_name='product_id', string='Sources', copy=True, track_visibility='onchange')

    source_count = fields.Integer(compute='_compute_source_count', string='Total sources')

    @api.depends('source_ids')
    def _compute_source_count(self):
        for rec in self:
            rec.source_count = sum(rec.source_ids.mapped('num'))

    # Beams tab
    beam_ids = fields.One2many(comodel_name='lighting.product.beam',
                               inverse_name='product_id', string='Beams', copy=True, track_visibility='onchange')

    beam_count = fields.Integer(compute='_compute_beam_count', string='Total beams')

    @api.depends('beam_ids')
    def _compute_beam_count(self):
        for rec in self:
            rec.beam_count = sum(rec.beam_ids.mapped('num'))

    # notes tab
    note_ids = fields.One2many(comodel_name='lighting.product.notes',
                               inverse_name='product_id',
                               string='Notes', copy=True,
                               track_visibility='onchange')

    # Attachment tab
    attachment_ids = fields.One2many(comodel_name='lighting.attachment',
                                     inverse_name='product_id', string='Attachments', copy=True,
                                     track_visibility='onchange')
    attachment_count = fields.Integer(compute='_compute_attachment_count', string='Attachment(s)')

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = self.env['lighting.attachment'].search_count([('product_id', '=', record.id)])

    # Optional accesories tab
    optional_ids = fields.Many2many(comodel_name='lighting.product', relation='lighting_product_optional_rel',
                                    column1="product_id", column2='optional_id',
                                    string='Recommended accessories', track_visibility='onchange')

    parent_optional_accessory_product_count = fields.Integer(compute='_compute_parent_optional_accessory_product_count')

    @api.depends('optional_ids')
    def _compute_parent_optional_accessory_product_count(self):
        for record in self:
            record.parent_optional_accessory_product_count = self.env['lighting.product'] \
                .search_count([('optional_ids', '=', record.id)])

    is_optional_accessory = fields.Boolean(string='Is recommended accessory',
                                           compute='_compute_is_optional_accessory',
                                           search='_search_is_optional_accessory')

    @api.depends('optional_ids')
    def _compute_is_optional_accessory(self):
        for rec in self:
            parent_ids = self.env['lighting.product'].search([('optional_ids', '=', rec.id)])
            if parent_ids:
                rec.is_optional_accessory = True

    def _search_is_optional_accessory(self, operator, value):
        ids = self.env['lighting.product'] \
            .search([('optional_ids', '!=', False)]).mapped('optional_ids.id')

        return [('id', 'in', ids)]

    # Required accessories tab
    required_ids = fields.Many2many(comodel_name='lighting.product', relation='lighting_product_required_rel',
                                    column1="product_id", column2='required_id',
                                    string='Mandatory accessories', track_visibility='onchange')

    parent_required_accessory_product_count = fields.Integer(compute='_compute_parent_required_accessory_product_count')

    @api.depends('required_ids')
    def _compute_parent_required_accessory_product_count(self):
        for record in self:
            record.parent_required_accessory_product_count = self.env['lighting.product'] \
                .search_count([('required_ids', '=', record.id)])

    is_required_accessory = fields.Boolean(string='Is required accessory',
                                           compute='_compute_is_required_accessory',
                                           search='_search_is_required_accessory')

    @api.depends('required_ids')
    def _compute_is_required_accessory(self):
        for rec in self:
            parent_ids = self.env['lighting.product'].search([('required_ids', '=', rec.id)])
            if parent_ids:
                rec.is_required_accessory = True

    def _search_is_required_accessory(self, operator, value):
        ids = self.env['lighting.product'] \
            .search([('required_ids', '!=', False)]).mapped('required_ids.id')

        return [('id', 'in', ids)]

    # Substitutes tab
    substitute_ids = fields.Many2many(comodel_name='lighting.product', relation='lighting_product_substitute_rel',
                                      column1='product_id', column2='substitute_id',
                                      string='Substitutes', track_visibility='onchange')

    # logistics tab
    tariff_item = fields.Char(string="Tariff item", track_visibility='onchange')
    assembler_id = fields.Many2one(comodel_name='lighting.assembler', ondelete='restrict',
                                   string='Assembler', track_visibility='onchange')
    supplier_ids = fields.One2many(comodel_name='lighting.product.supplier', inverse_name='product_id',
                                   string='Suppliers', copy=True, track_visibility='onchange')

    ibox_weight = fields.Float(string='IBox weight (Kg)', track_visibility='onchange')
    ibox_volume = fields.Float(string='IBox volume (cm³)', track_visibility='onchange')
    ibox_length = fields.Float(string='IBox length (cm)', track_visibility='onchange')
    ibox_width = fields.Float(string='IBox width (cm)', track_visibility='onchange')
    ibox_height = fields.Float(string='IBox height (cm)', track_visibility='onchange')

    mbox_qty = fields.Integer(string='Masterbox quantity', track_visibility='onchange')
    mbox_weight = fields.Float(string='Masterbox weight (kg)', track_visibility='onchange')
    mbox_length = fields.Float(string='Masterbox length (cm)', track_visibility='onchange')
    mbox_width = fields.Float(string='Masterbox width (cm)', track_visibility='onchange')
    mbox_height = fields.Float(string='Masterbox height (cm)', track_visibility='onchange')

    # inventory tab
    onhand_qty = fields.Float(string="On hand", readonly=True,
                              required=True, default=0,
                              copy=False)
    commited_qty = fields.Float(string="Commited", readonly=True,
                                required=True, default=0,
                                copy=False)
    available_qty = fields.Float(string="Available", readonly=True,
                                 required=True, default=0,
                                 copy=False)

    capacity_qty = fields.Float(string="Capacity", readonly=True,
                                required=True, default=0,
                                copy=False)

    onorder_qty = fields.Float(string="On order", readonly=True,
                               required=True, default=0,
                               copy=False)

    stock_future_qty = fields.Float(string="Future stock", readonly=True,
                                    required=True, default=0,
                                    copy=False)
    stock_future_date = fields.Date(string="Future stock date", readonly=True,
                                    copy=False)
    last_purchase_date = fields.Date(string="Last purchase date", readonly=True,
                                     copy=False)

    # marketing tab
    state_marketing = fields.Selection(
        selection=STATES_MARKETING,
        string='Marketing status', track_visibility='onchange')

    on_request = fields.Boolean(string='On request', track_visibility='onchange')

    effective_date = fields.Date(string='Effective date', track_visibility='onchange')

    price = fields.Float(string='Price', readonly=True)
    price_currency_id = fields.Many2one(string='Price currency',
                                        comodel_name='res.currency',
                                        readonly=True)

    cost = fields.Float(string='Cost', readonly=True, groups='lighting.group_lighting_user')
    cost_currency_id = fields.Many2one(string='Cost currency',
                                       comodel_name='res.currency',
                                       readonly=True,
                                       groups='lighting.group_lighting_user')

    marketing_comments = fields.Char(string='Comments', track_visibility='onchange')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_review', 'To review'),
        ('published', 'Published'),
    ], string='Status', default='draft', readonly=False, required=True, copy=False, track_visibility='onchange')

    @api.multi
    @api.constrains('reference')
    def _check_reference_spaces(self):
        for rec in self:
            if rec.reference != rec.reference.strip():
                raise ValidationError(
                    _('The reference has trailing and/or leading spaces, plese remove them before saving.'))

    @api.multi
    @api.constrains('catalog_ids')
    def _check_catalog_ids(self):
        # TODO remove this constrain and change the catalog_ids attribute to
        # many2one
        for rec in self:
            if len(rec.catalog_ids) != 1:
                raise ValidationError(
                    _('Only one catalog is allowed per product'))

    @api.multi
    @api.constrains('is_composite', 'required_ids')
    def _check_composite_product(self):
        for rec in self:
            if not rec.is_composite and rec.required_ids:
                raise ValidationError(
                    _("Only the composite products can have required accessories. Enable 'is_composite' "
                      "field or remove the required accessories associated."))

            if rec.is_composite and not rec.required_ids:
                raise ValidationError(
                    _("You cannot have a composite product without required accessories"))

    @api.constrains('product_group_id')
    def _check_product_group(self):
        if self.product_group_id.child_ids:
            raise ValidationError(_("You cannot assign products to a grup with childs. "
                                    "The group must not have childs and be empty or already contain products"))

    @api.constrains('configurator', 'product_group_id')
    def _check_configurator_product_group(self):
        if self.configurator and self.product_group_id:
            raise ValidationError(_("Products with configurator cannot belong to a group"))

    @api.multi
    @api.constrains('optional_ids', 'required_ids')
    def _check_composite_product(self):
        for rec in self:
            if rec in rec.required_ids:
                raise ValidationError(
                    _("The current reference cannot be defined as a required accessory"))

            if rec in rec.optional_ids:
                raise ValidationError(
                    _("The current reference cannot be defined as a recomended accessory"))

    @api.constrains('description')
    def _check_description_updated(self):
        self._update_computed_descriptions(exclude_lang=[self.env.lang])

    @api.constrains('state', 'family_ids', 'category_id')
    def _check_published_mandatory_fields(self):
        for rec in self:
            if rec.state == 'published':
                if not rec.family_ids or not rec.category_id or not rec.location_ids:
                    raise ValidationError("The Family, Category and Locations are mandatory in Published state")

    def _update_with_check(self, values, key, value):
        if key not in values:
            values[key] = value
        else:
            if values[key] != value:
                raise ValidationError(
                    _("Inconsistency due to multi nature of the method, not all records have the "
                      "same values"))

    def _check_state_marketing_stock(self, values):
        new_values = {}
        current_state, new_state = self.state_marketing, values.get('state_marketing', self.state_marketing)
        current_state_str, new_state_str = [STATE_NAME_MAP(self)[x] for x in [current_state, new_state]]
        new_stock = sum([values[f] if f in values else self[f] for f in ('available_qty', 'stock_future_qty')])
        if current_state in C_STATES:
            if new_state in ES_MAP:
                if new_stock == 0:
                    raise ValidationError(
                        _("You cannot change the state from '%s' to '%s' if the product has no stock") % (
                            current_state_str, new_state_str))
            elif new_state in D_MAP:
                if new_stock != 0:
                    raise ValidationError(
                        _("You cannot change the state from '%s' to '%s' if the product has stock (%g)") % (
                            current_state_str, new_state_str, new_stock))
            elif new_state in C_STATES:
                pass
            else:
                raise ValidationError(_("Transition from '%s' to '%s' not allowed") % (
                    current_state_str, new_state_str))
        elif current_state in ES_MAP:
            if new_state in C_STATES:
                if new_state and new_stock == 0:
                    raise ValidationError(
                        _("You cannot change the state from '%s' to '%s' if the product has no stock") % (
                            current_state_str, new_state_str))
            elif new_state == ES_MAP[current_state]:
                if new_stock != 0:
                    raise ValidationError(
                        _("You cannot change the state from '%s' to '%s' if the product has stock (%g)") % (
                            current_state_str, new_state_str, new_stock))
            elif new_state == current_state:
                if new_stock == 0:
                    self._update_with_check(new_values, 'state_marketing', ES_MAP[current_state])
            elif new_state in ES_MAP:
                pass
            elif not new_state:
                pass
            else:
                raise ValidationError(_("Transition from '%s' to '%s' not allowed") % (
                    current_state_str, new_state_str))
        elif current_state in D_MAP:
            if new_state in C_STATES:
                pass
            elif new_state == D_MAP[current_state]:
                if new_stock == 0:
                    raise ValidationError(
                        _("You cannot change the state from '%s' to '%s' if the product has no stock") % (
                            current_state_str, new_state_str))
            elif new_state == current_state:
                if new_stock != 0:
                    self._update_with_check(new_values, 'state_marketing', D_MAP[current_state])
            elif new_state in D_MAP:
                pass
            elif not new_state:
                pass
            else:
                raise ValidationError(_("Transition from '%s' to '%s' not allowed") % (
                    current_state_str, new_state_str))
        else:
            raise ValidationError(_("State '%s' not exists") % (current_state_str,))
        return new_values

    @api.multi
    def copy(self, default=None):
        self.ensure_one()

        ## generate non duplicated new reference
        reference_tmp = self.reference
        while True:
            product_ids = self.env[self._name].search([('reference', '=', reference_tmp)])
            if len(product_ids) == 0:
                break
            reference_tmp = '%s (copy)' % reference_tmp

        default = dict(default or {},
                       reference=reference_tmp,
                       ean=False,
                       )

        return super(LightingProduct, self).copy(default)

    @api.multi
    def write(self, values):
        if 'reference' in values and 'default_code' not in values:
            values['default_code'] = values['reference']
        if 'price' in values and 'lst_price' not in values:
            values['lst_price'] = values['price']
        result = True
        for rec in self:
            new_values = rec._check_state_marketing_stock(values)
            if new_values:
                values.update(new_values)
            original_description = rec.description
            result &= super(LightingProduct, rec).write(values)
            if rec.description != original_description:
                for lang in self.env['res.lang'].search([]):
                    rec = rec.with_context(lang=lang.code)
                    rec.name = rec.description or rec.description_manual or rec.reference
        return result

    @api.model
    def create(self, values):
        product_tmp = self.env['lighting.product'].new(values)
        values.update({
            'name': product_tmp.description or product_tmp.description_manual or values['reference'],
            'default_code': values['reference'],
            'lst_price': 0
        })
        new_values = self._check_state_marketing_stock(values)
        if new_values:
            values.update(new_values)
        return super(LightingProduct, self).create(values)

    @api.multi
    def unlink(self):
        product_tmpl = self.mapped('odoop_id.product_tmpl_id')
        res = super(LightingProduct, self).unlink()
        res &= product_tmpl.unlink()
        return res
