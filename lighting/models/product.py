# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
# TODO :Deleted from security:
#  access_product_product_price_history_guest,product.product
#  guest,product.model_product_price_history,lighting.group_lighting_guest,1,0,0,0
#  access_product_product_price_history_user,product.product
#  user,product.model_product_price_history,lighting.group_lighting_user,1,1,1,1
# It's ok?
import logging
import re
from collections import OrderedDict

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

YESNO = [
    ("Y", _("Yes")),
    ("N", _("No")),
]

STATES_MARKETING = [
    ("O", "Online"),
    ("N", "New"),
    ("C", "Cataloged"),
    ("ES", "Until end of stock"),
    ("ESH", "Until end of stock (historical)"),
    ("D", "Discontinued"),
    ("H", "Historical"),
]

ES_MAP = {"ES": "D", "ESH": "H"}
D_MAP = {v: k for k, v in ES_MAP.items()}
C_STATES = {"O", "N", "C", False}


def _get_state_name_map(x):
    return {
        False: "",
        **dict(
            x.fields_get("state_marketing", "selection")["state_marketing"]["selection"]
        ),
    }


class LightingProduct(models.Model):
    _name = "lighting.product"
    _description = "Product"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _inherits = {"product.product": "odoop_id"}
    _rec_name = "reference"
    _order = "sequence,reference"

    # binding fields
    odoop_id = fields.Many2one(
        comodel_name="product.product",
        string="Odoo Product ID",
        required=True,
        ondelete="cascade",
    )

    # TODO: This reference can be a product.default_code?
    # Common data
    reference = fields.Char(
        required=True,
        tracking=True,
    )

    # image: all image fields are base64 encoded and PIL-supported
    image_small = fields.Image(
        string="Small-sized image",
        attachment=True,
        max_width=128,
        max_height=128,
        store=True,
        compute="_compute_images",
    )
    image_medium = fields.Image(
        string="Medium-sized image",
        attachment=True,
        max_width=512,
        max_height=512,
        store=True,
        compute="_compute_images",
    )

    @api.depends(
        "attachment_ids.datas_location",
        "attachment_ids.datas",
        "attachment_ids.datas_url",
        "attachment_ids.image_small",
        "attachment_ids.image_medium",
        "attachment_ids.sequence",
        "attachment_ids.type_id",
        "attachment_ids.type_id.is_image",
    )
    def _compute_images(self):
        for rec in self:
            if rec.attachment_ids:
                resized_image = rec.attachment_ids.get_main_resized_image()
                if resized_image:
                    rec.image_medium = resized_image["image_medium"]
                    rec.image_small = resized_image["image_small"]
                else:
                    rec.image_medium = False
                    rec.image_small = False
            else:
                rec.image_medium = False
                rec.image_small = False

    description = fields.Char(
        compute="_compute_description",
        readonly=True,
        help="Description dynamically generated from product data",
        translate=True,
        store=True,
        tracking=True,
    )

    @api.depends(
        "category_id.name",
        "category_id.description_text",
        "category_id.effective_description_dimension_ids",
        "model_id",
        "model_id.name",
        "family_ids.name",
        "catalog_ids.description_show_ip",
        "catalog_ids.description_show_ip_condition",
        "sealing_id",
        "sealing_id.name",
        "diffusor_material_ids",
        "diffusor_material_ids.name",
        "diffusor_material_ids.is_glass",
        "sensor_ids",
        "sensor_ids.name",
        "dimmable_ids.name",
        "dimension_ids",
        "dimension_ids.type_id",
        "dimension_ids.type_id.code",
        "dimension_ids.value",
        "source_ids.sequence",
        "source_ids.lampholder_id.code",
        "source_ids.line_ids.sequence",
        "source_ids.line_ids.type_id.code",
        "source_ids.line_ids.type_id.is_integrated",
        "source_ids.line_ids.type_id.is_led",
        "source_ids.line_ids.type_id.description_text",
        "source_ids.line_ids.is_lamp_included",
        "source_ids.line_ids.wattage",
        "source_ids.line_ids.wattage_magnitude",
        "source_ids.line_ids.cri_min",
        "source_ids.line_ids.special_spectrum_id",
        "source_ids.line_ids.special_spectrum_id.name",
        "source_ids.line_ids.is_color_temperature_flux_tunable",
        "source_ids.line_ids.color_temperature_flux_ids",
        "source_ids.line_ids.color_temperature_flux_ids.color_temperature_id",
        "source_ids.line_ids.color_temperature_flux_ids.color_temperature_id.value",
        "source_ids.line_ids.color_temperature_flux_ids.nominal_flux",
        "beam_ids.dimension_ids",
        "beam_ids.dimension_ids.type_id",
        "beam_ids.dimension_ids.type_id.code",
        "beam_ids.dimension_ids.type_id.uom",
        "beam_ids.dimension_ids.value",
        "finish_id.name",
        "finish2_id.name",
        "inclination_angle_max",
    )
    def _compute_description(self):
        for rec in self:
            for lang in self.env["res.lang"].search([]):
                # rec.with_context(lang_aux=lang.code)
                rec.with_context(lang=lang.code).description = rec.with_context(
                    lang=lang.code
                )._generate_description()

    def _update_category(self, data):
        self.ensure_one()
        if self.category_id:
            data.append(self.category_id.description_text or self.category_id.name)
        return data

    def _update_inclination_angle_max(self, data):
        self.ensure_one()
        if self.inclination_angle_max:
            data.append("tilt")
        return data

    def _update_family(self, data):
        self.ensure_one()
        if self.family_ids:
            data.append(
                ",".join(
                    map(
                        lambda x: x.upper(),
                        self.family_ids.sorted(lambda x: (x.sequence, x.name)).mapped(
                            "name"
                        ),
                    )
                )
            )
        return data

    def _update_model(self, data):
        self.ensure_one()
        if self.model_id:
            data.append(self.model_id.name)
        return data

    def _update_sealing(self, data):
        self.ensure_one()
        if self.sealing_id:
            sealing_id = self.sealing_id
            for catalog in self.catalog_ids:
                if catalog.description_show_ip:
                    if self.sealing_id:
                        break
                else:
                    ip_condition = (
                        catalog.description_show_ip_condition
                        and catalog.description_show_ip_condition.strip()
                        or None
                    )
                    if ip_condition:
                        try:
                            expr = ip_condition % dict(
                                value="'%s'" % self.sealing_id.name
                            )
                            if safe_eval(expr):
                                break
                        except ValueError as e:
                            raise UserError(
                                _("Incorrect format expression: %s") % expr,
                            ) from e
            else:
                sealing_id = None
            if sealing_id:
                data.append(sealing_id.name)
        return data

    def _update_dimmable(self, data):
        self.ensure_one()
        if self.dimmable_ids:
            data.append(
                ",".join(self.dimmable_ids.sorted(lambda x: x.name).mapped("name"))
            )
        return data

    def _update_beams(self, data):
        self.ensure_one()
        if self.beam_ids:
            beam_angle_display = self.beam_ids.get_beam_angle_display()
            if beam_angle_display:
                data.append(beam_angle_display)
        return data

    def _update_sensors(self, data):
        self.ensure_one()
        if self.sensor_ids:
            data.append(
                ",".join(self.sensor_ids.sorted(lambda x: x.name).mapped("name"))
            )
        return data

    def _update_charger_connector_type(self, data):
        self.ensure_one()
        if self.charger_connector_type_id:
            data.append(self.charger_connector_type_id.name)
        return data

    def _update_effective_description_dimensions(self, data):
        self.ensure_one()
        if self.category_id:
            if self.category_id.effective_description_dimension_ids:
                if self.dimension_ids:
                    dimensions = self.dimension_ids.filtered(
                        lambda x: x.type_id
                        in self.category_id.effective_description_dimension_ids
                    )
                    if dimensions:
                        data.append(dimensions.get_value_display(spaces=False))
        return data

    def _update_diffusor_material(self, data):
        self.ensure_one()
        if self.family_ids:
            if set(self.family_ids.mapped("code")) & {"984", "GLOB", "129", "393"}:
                diameter_dimension = self.dimension_ids.filtered(
                    lambda x: x.type_id.code == "DIAMETERMM"
                )
                if diameter_dimension:
                    data.append(
                        "\u2300%s" % diameter_dimension.get_value_display(spaces=False)
                    )
            if set(self.family_ids.mapped("code")) & {"984", "264", "096"}:
                glass_diffuser_material = self.diffusor_material_ids.filtered(
                    lambda x: x.is_glass
                )
                if glass_diffuser_material:
                    data.append(",".join(glass_diffuser_material.mapped("name")))
        return data

    def _update_multiple_beams(self, data):
        self.ensure_one()
        if self.beam_count == 2:
            data.append("up-down")
        return data

    def _update_finish(self, data, show_variant_data):
        self.ensure_one()
        if show_variant_data and self.finish_id:
            data.append(self.finish_id.name)
        return data

    def _update_finish2(self, data):
        self.ensure_one()
        if self.finish2_id:
            data.append(self.finish2_id.name)
        return data

    def _get_line_data(self, data_lines, line, ignore_nulls=False):
        data_line = []
        data_line.append(line.type_id.description_text or line.type_id.code)

        wattage_total_display = line.prepare_wattage_str(
            mult=line.source_id.num or 1, is_max_wattage=False
        )
        if wattage_total_display:
            data_line.append(wattage_total_display)

        if line.color_temperature_flux_ids:
            luminous_flux_display = line.with_context(
                ignore_nulls=ignore_nulls
            ).luminous_flux_display
            if luminous_flux_display:
                data_line.append(luminous_flux_display)

        if line.cri_min:
            data_line.append("CRI%i" % line.cri_min)

        if line.color_temperature_flux_ids:
            color_temperature_display = line.with_context(
                ignore_nulls=ignore_nulls
            ).color_temperature_display
            if color_temperature_display:
                data_line.append(color_temperature_display)

        if not line.color_temperature_flux_ids:
            if line.is_led and line.special_spectrum_id:
                data_line.append(line.special_spectrum_id.name)

        if data_line:
            data_lines.append(" ".join(data_line))
        return data_lines

    # TODO:REVIEW:Test for this function
    def _generate_description(self, show_variant_data=True):  # noqa: C901
        self.ensure_one()
        _logger.info(
            _("Generating %(lang)s description for %(reference)s")
            % {
                "lang": self.env.context.get("lang") or "en_US",
                "reference": self.reference,
            }
        )
        data = []
        # data = [
        #     self._update_beams,
        # ]
        # data.append(self._update_beams)
        data = self._update_category(data)
        data = self._update_inclination_angle_max(data)
        data = self._update_family(data)
        data = self._update_model(data)
        data = self._update_sealing(data)
        data = self._update_dimmable(data)

        # data = list(map(x(), data))
        data_sources = []
        for source in self.source_ids.sorted(lambda x: x.sequence):
            data_source = []
            if source.lampholder_id:
                data_source.append(source.lampholder_id.code)
            type_d = {}
            for line in source.line_ids.sorted(
                lambda x: (x.type_id.is_integrated, x.sequence)
            ):
                is_integrated = line.type_id.is_integrated
                type_d.setdefault(is_integrated, []).append(line)

            data_lines = []
            for is_integrated, lines in type_d.items():
                if is_integrated:
                    for line in lines:
                        data_lines = self._get_line_data(
                            data_lines, line, ignore_nulls=True
                        )
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
                                self._get_line_data(data_lines, line)
                        else:
                            wattage_d = {}
                            for line in llines:
                                if line.wattage > 0 and line.wattage_magnitude:
                                    if line.wattage_magnitude not in wattage_d:
                                        wattage_d[line.wattage_magnitude] = []
                                    wattage_d[line.wattage_magnitude].append(line)

                            for wlines in wattage_d.values():
                                line_max = sorted(
                                    wlines, key=lambda x: x.wattage, reverse=True
                                )[0]
                                wattage_total_display = line_max.prepare_wattage_str(
                                    mult=line_max.source_id.num or 1,
                                    is_max_wattage=False,
                                )
                                if wattage_total_display:
                                    data_lines.append(wattage_total_display)

            if data_lines:
                data_source.append(",".join(data_lines))
            if data_source:
                data_sources.append(" ".join(data_source))
        if data_sources:
            data.append("+".join(data_sources))

        data = self._update_beams(data)
        data = self._update_sensors(data)
        data = self._update_charger_connector_type(data)
        data = self._update_effective_description_dimensions(data)
        data = self._update_diffusor_material(data)
        data = self._update_multiple_beams(data)
        data = self._update_finish(data, show_variant_data)
        data = self._update_finish2(data)

        if data:
            return " ".join(data)
        else:
            return None

    description_manual = fields.Char(
        string="Description (manual)",
        help="Manual description",
        translate=True,
        tracking=True,
    )
    ean = fields.Char(
        string="EAN",
        required=False,
        readonly=True,
        tracking=True,
    )
    product_group_id = fields.Many2one(
        comodel_name="lighting.product.group",
        string="Group",
        ondelete="restrict",
        tracking=True,
    )
    family_ids = fields.Many2many(
        comodel_name="lighting.product.family",
        relation="lighting_product_family_rel",
        string="Families",
        required=False,
        tracking=True,
    )
    catalog_ids = fields.Many2many(
        comodel_name="lighting.catalog",
        relation="lighting_product_catalog_rel",
        string="Catalogs",
        required=True,
        tracking=True,
    )
    category_id = fields.Many2one(
        comodel_name="lighting.product.category",
        required=False,
        ondelete="restrict",
        tracking=True,
    )
    category_completename = fields.Char(
        string="Category (complete name)",
        compute="_compute_category_complete_name",
        inverse="_inverse_category_complete_name",
    )

    def _compute_category_complete_name(self):
        for rec in self:
            rec.category_completename = (
                rec.category_id and rec.category_id.complete_name or False
            )

    def _inverse_category_complete_name(self):
        for rec in self:
            if rec.category_completename:
                category_leafs = self.env[
                    "lighting.product.category"
                ].get_leaf_from_complete_name(rec.category_completename)
                if category_leafs:
                    rec.category_id = category_leafs[0]
                else:
                    raise ValidationError(
                        _("Category with complete name '%s' does not exist")
                        % rec.category_completename
                    )
            else:
                rec.category_id = False

    model_id = fields.Many2one(
        comodel_name="lighting.product.model",
    )
    is_accessory = fields.Boolean(
        compute="_compute_is_accessory",
        search="_search_is_accessory",
        readonly=True,
    )

    @api.depends("category_id", "category_id.is_accessory")
    def _compute_is_accessory(self):
        for rec in self:
            if rec.category_id:
                rec.is_accessory = rec.category_id._get_is_accessory()
            else:
                rec.is_accessory = False

    def _search_is_accessory(self, operator, value):
        ids = []
        for prod in self.env["lighting.product"].search(
            [
                ("category_id", "!=", False),
            ]
        ):
            is_accessory = prod.category_id._get_is_accessory()
            if operator == "=":
                if is_accessory == value:
                    ids.append(prod.id)
            elif operator == "!=":
                if is_accessory != value:
                    ids.append(prod.id)
            else:
                raise ValidationError(_("Operator '%s' not supported") % operator)
        return [("id", "in", ids)]

    is_composite = fields.Boolean(
        default=False,
    )

    # TODO: REVIEW THIS CONSTRAIN INSTEAD OF ONCHANGE
    @api.constrains("is_composite", "required_ids")
    def _check_is_composite_required_ids(self):
        for rec in self:
            if not rec.is_composite and rec.required_ids:
                raise ValidationError(_("It's not possible "))

    # @api.onchange("is_composite")
    # def _onchange_is_composite(self):
    #     if not self.is_composite and self.required_ids:
    #         self.is_composite = True
    #         return {
    #             "warning": {
    #                 "title": "Warning",
    #                 "message": _(
    #                     "You cannot change this while the product "
    #                     "has necessary accessories assigned"
    #                 ),
    #             },
    #         }

    parents_brand_ids = fields.Many2many(
        comodel_name="lighting.catalog",
        compute="_compute_parents_brands",
        readonly=True,
        string="Parents brands",
        help="Brands of the products that one of their optional and/or "
        "required accessories is the current product",
    )

    @api.depends("optional_ids", "required_ids")
    def _compute_parents_brands(self):
        for rec in self:
            parents = self.env["lighting.product"].search(
                [
                    "|",
                    ("optional_ids", "=", rec.id),
                    ("required_ids", "=", rec.id),
                ]
            )
            if parents:
                brand_ids = list(set(parents.mapped("catalog_ids.id")))
                rec.parents_brand_ids = [(6, False, brand_ids)]
            else:
                rec.parents_brand_ids = False

    last_update = fields.Date(
        string="Last modified on",
        tracking=True,
    )
    configurator = fields.Boolean(
        required=True,
        default=False,
        tracking=True,
    )
    sequence = fields.Integer(
        required=True,
        default=1,
        help="The sequence field is used to define order",
        tracking=True,
    )

    _sql_constraints = [
        ("reference_uniq", "unique (reference)", "The reference must be unique!"),
        ("ean_uniq", "unique (ean)", "The EAN must be unique!"),
    ]

    # Description tab
    location_ids = fields.Many2many(
        comodel_name="lighting.product.location",
        relation="lighting_product_location_rel",
        string="Locations",
        required=False,
        tracking=True,
    )
    installation_ids = fields.Many2many(
        comodel_name="lighting.product.installation",
        relation="lighting_product_installation_rel",
        string="Installations",
        tracking=True,
    )

    application_ids = fields.Many2many(
        comodel_name="lighting.product.application",
        relation="lighting_product_application_rel",
        string="Applications",
        tracking=True,
    )
    finish_id = fields.Many2one(
        comodel_name="lighting.product.finish",
        ondelete="restrict",
        tracking=True,
    )
    finish_prefix = fields.Char(
        compute="_compute_finish_prefix",
    )

    def _compute_finish_prefix(self):
        for rec in self:
            has_sibling = False
            m = re.match(r"^(.+)-.{2}$", rec.reference)
            if m:
                prefix = m.group(1)
                product_siblings = self.search(
                    [
                        ("reference", "=like", "%s-__" % prefix),
                        ("id", "!=", rec.id),
                    ]
                )
                if product_siblings:
                    rec.finish_prefix = prefix
                    has_sibling = True
            rec.finish_prefix = rec.reference if not has_sibling else False

    finish2_id = fields.Many2one(
        comodel_name="lighting.product.finish",
        ondelete="restrict",
        string="Finish 2",
        tracking=True,
    )
    ral_id = fields.Many2one(
        comodel_name="lighting.product.ral",
        ondelete="restrict",
        string="RAL",
        tracking=True,
    )
    body_material_ids = fields.Many2many(
        comodel_name="lighting.product.material",
        relation="lighting_product_body_material_rel",
        tracking=True,
    )
    lampshade_material_ids = fields.Many2many(
        comodel_name="lighting.product.material",
        relation="lighting_product_lampshade_material_rel",
        tracking=True,
    )
    # TODO: Migration Script. Diffusor is a typo. migrate to diffuser
    diffusor_material_ids = fields.Many2many(
        comodel_name="lighting.product.material",
        relation="lighting_product_diffusor_material_rel",
        string="Diffuser material",
        tracking=True,
    )
    frame_material_ids = fields.Many2many(
        comodel_name="lighting.product.material",
        relation="lighting_product_frame_material_rel",
        tracking=True,
    )
    reflector_material_ids = fields.Many2many(
        comodel_name="lighting.product.material",
        relation="lighting_product_reflector_material_rel",
        tracking=True,
    )
    blade_material_ids = fields.Many2many(
        comodel_name="lighting.product.material",
        relation="lighting_product_blade_material_rel",
        tracking=True,
    )

    sealing_id = fields.Many2one(
        comodel_name="lighting.product.sealing",
        ondelete="restrict",
        tracking=True,
    )
    sealing2_id = fields.Many2one(
        comodel_name="lighting.product.sealing",
        ondelete="restrict",
        string="Sealing 2",
        tracking=True,
    )

    ik = fields.Selection(
        selection=[("%02d" % x, "%02d" % x) for x in range(11)],
        string="IK",
        tracking=True,
    )

    static_pressure = fields.Float(
        string="Static pressure (kg)",
        tracking=True,
    )
    dynamic_pressure = fields.Float(
        string="Dynamic pressure (kg)",
        tracking=True,
    )
    dynamic_pressure_velocity = fields.Float(
        string="Dynamic pressure (km/h)",
        tracking=True,
    )
    corrosion_resistance = fields.Selection(
        selection=YESNO,
        string="Corrosion resistance",
        tracking=True,
    )
    technical_comments = fields.Char(
        tracking=True,
    )

    # electrical characteristics tab
    protection_class_id = fields.Many2one(
        comodel_name="lighting.product.protectionclass",
        ondelete="restrict",
        tracking=True,
    )
    frequency_id = fields.Many2one(
        comodel_name="lighting.product.frequency",
        ondelete="restrict",
        string="Frequency (Hz)",
        tracking=True,
    )
    dimmable_ids = fields.Many2many(
        comodel_name="lighting.product.dimmable",
        relation="lighting_product_dimmable_rel",
        string="Dimmables",
        tracking=True,
    )
    auxiliary_equipment_ids = fields.Many2many(
        comodel_name="lighting.product.auxiliaryequipment",
        relation="lighting_product_auxiliary_equipment_rel",
        string="Auxiliary gear",
        tracking=True,
    )
    auxiliary_equipment_model_ids = fields.One2many(
        comodel_name="lighting.product.auxiliaryequipmentmodel",
        inverse_name="product_id",
        string="Auxiliary gear code",
        copy=True,
        tracking=True,
    )
    auxiliary_equipment_model_alt = fields.Char(
        string="Alternative auxiliary gear code",
        tracking=True,
    )
    input_voltage_id = fields.Many2one(
        comodel_name="lighting.product.voltage",
        ondelete="restrict",
        tracking=True,
    )
    input_current = fields.Integer(
        string="Input current (mA)",
        tracking=True,
    )
    output_voltage_id = fields.Many2one(
        comodel_name="lighting.product.voltage",
        ondelete="restrict",
        tracking=True,
    )
    output_current = fields.Integer(
        string="Output current (mA)",
        tracking=True,
    )

    total_wattage = fields.Float(
        string="Total wattage (W)",
        help="Total power consumed by the luminaire",
        tracking=True,
        compute="_compute_total_wattage",
        readonly=False,
        store=True,
    )
    # TODO: mirar de fer una constrain per a que no es pugui escriure aquest camp si
    #  el total_wattage_auto es True. Podriem fer una constrain simple??
    #  saltaria al modificar el valor pel compute??

    # TODO: this should be replaces by only total_wattage computed with readonly=False
    #   when migrating to version >=13.0
    # TODO: delete this field in migration script
    # total_wattage_sources = fields.Float(
    #     compute="_compute_total_wattage_sources",
    #     store=True,
    # )

    @api.depends(
        "total_wattage_auto",
        "source_ids.line_ids.wattage",
        "source_ids.line_ids.type_id",
        "source_ids.line_ids.type_id.is_integrated",
        "source_ids.line_ids.is_lamp_included",
    )
    def _compute_total_wattage(self):
        for rec in self:
            if rec.total_wattage_auto:
                total_wattage = 0
                line_l = rec.source_ids.mapped("line_ids").filtered(
                    lambda x: x.is_integrated or x.is_lamp_included
                )
                for line in line_l:
                    if line.wattage <= 0:
                        raise ValidationError(
                            _("%(name)s: The source line %(type)s has invalid wattage")
                            % {
                                "name": rec.display_name,
                                "type": line.type_id.display_name,
                            }
                        )
                    total_wattage += line.source_id.num * line.wattage
                rec.total_wattage = total_wattage

    # TODO: delete this field in migration script
    # total_wattage = fields.Float(
    #     string="Total wattage (W)",
    #     help="Total power consumed by the luminaire",
    #     tracking=True,
    # )
    total_wattage_auto = fields.Boolean(
        string="Autocalculate",
        help="Autocalculate total wattage",
        default=True,
        tracking=True,
    )
    power_factor_min = fields.Float(
        string="Minimum power factor",
        tracking=True,
    )
    power_switches = fields.Integer(
        help="Number of power switches",
        tracking=True,
    )
    usb_ports = fields.Integer(
        string="USB ports charging devices",
        help="Number of USB charging ports",
        tracking=True,
    )
    usb_voltage = fields.Float(
        string="USB charging voltage (V)",
        tracking=True,
    )
    usb_current = fields.Float(
        string="USB charging current (mA)",
        tracking=True,
    )
    charger_connector_type_id = fields.Many2one(
        comodel_name="lighting.product.connectortype",
        ondelete="restrict",
        tracking=True,
    )
    sensor_ids = fields.Many2many(
        comodel_name="lighting.product.sensor",
        relation="lighting_product_sensor_rel",
        string="Sensors",
        tracking=True,
    )
    rechargeable_type = fields.Selection(
        selection=[
            ("solar", "Solar"),
            ("charger", "With charger"),
            ("solarcharger", "Solar/With charger"),
        ],
        string="Rechargeable",
        tracking=True,
    )
    battery_autonomy = fields.Float(
        string="Battery autonomy (h)",
        tracking=True,
    )
    battery_charge_time = fields.Float(
        string="Battery charge time (h)",
        tracking=True,
    )
    battery_charge_capacity = fields.Integer(
        string="Battery charge capacity (mAH)",
        tracking=True,
    )
    battery_output_voltage = fields.Float(
        string="Battery output voltage (V)",
        digits=(5, 1),
        tracking=True,
    )
    surface_temperature = fields.Float(
        string="Surface temperature (ºC)",
        tracking=True,
    )
    operating_temperature_min = fields.Float(
        string="Minimum operating temperature (ºC)",
        tracking=True,
    )
    operating_temperature_max = fields.Float(
        string="Maximum operating temperature (ºC)",
        tracking=True,
    )
    glow_wire_temperature = fields.Float(
        string="Glow wire temperature (ºC)",
        tracking=True,
    )

    # light characteristics tab
    ugr_max = fields.Integer(
        string="UGR",
        help="Maximum unified glare rating",
        tracking=True,
    )
    lifetime = fields.Integer(
        string="Lifetime (h)",
        tracking=True,
    )
    led_lifetime_l = fields.Integer(
        string="LED lifetime L",
        tracking=True,
    )
    led_lifetime_b = fields.Integer(
        string="LED lifetime B",
        tracking=True,
    )

    # Physical characteristics
    weight = fields.Float(
        string="Weight (kg)",
        tracking=True,
    )
    dimension_ids = fields.One2many(
        comodel_name="lighting.product.dimension",
        inverse_name="product_id",
        string="Dimensions",
        copy=True,
        tracking=True,
    )
    cutting_length = fields.Float(
        string="Cutting length (mm)",
        tracking=True,
    )
    cable_outlets = fields.Integer(
        help="Number of cable outlets",
        tracking=True,
    )
    lead_wire_length = fields.Float(
        string="Length of the lead wire supplied (mm)",
        tracking=True,
    )
    inclination_angle_max = fields.Float(
        string="Maximum tilt angle (º)",
        tracking=True,
    )
    rotation_angle_max = fields.Float(
        string="Maximum rotation angle (º)",
        tracking=True,
    )
    recessing_box_included = fields.Selection(
        selection=YESNO,
        string="Cut hole box included",
        tracking=True,
    )
    recess_dimension_ids = fields.One2many(
        comodel_name="lighting.product.recessdimension",
        inverse_name="product_id",
        string="Cut hole dimensions",
        copy=True,
        tracking=True,
    )
    ecorrae_category_id = fields.Many2one(
        comodel_name="lighting.product.ecorraecategory",
        ondelete="restrict",
        string="ECORRAE I category",
        tracking=True,
    )
    ecorrae2_category_id = fields.Many2one(
        comodel_name="lighting.product.ecorraecategory",
        ondelete="restrict",
        string="ECORRAE II category",
        tracking=True,
    )
    ecorrae = fields.Float(
        string="ECORRAE I",
        tracking=True,
    )
    ecorrae2 = fields.Float(
        string="ECORRAE II",
        tracking=True,
    )
    periodic_maintenance = fields.Selection(
        selection=YESNO,
        string="Periodic maintenance",
        tracking=True,
    )
    anchorage_included = fields.Selection(
        selection=YESNO,
        string="Anchorage included",
        tracking=True,
    )
    post_included = fields.Selection(
        selection=YESNO,
        string="Post included",
        tracking=True,
    )
    post_with_inspection_chamber = fields.Selection(
        selection=YESNO,
        string="Post with inspection chamber",
        tracking=True,
    )
    emergency_light = fields.Selection(
        selection=YESNO,
        help="Luminarie with emergency light",
        tracking=True,
    )
    average_emergency_time = fields.Float(
        string="Average emergency time (h)",
        tracking=True,
    )
    flammable_surfaces = fields.Selection(
        selection=YESNO,
        tracking=True,
    )
    photobiological_risk_group_id = fields.Many2one(
        comodel_name="lighting.product.photobiologicalriskgroup",
        ondelete="restrict",
        tracking=True,
    )
    mechanical_screwdriver = fields.Selection(
        selection=YESNO,
        string="Electric screwdriver",
        tracking=True,
    )
    fan_blades = fields.Integer(
        string="Fan blades",
        help="Number of fan blades",
        tracking=True,
    )
    fan_control = fields.Selection(
        selection=[("remote", "Remote control"), ("wall", "Wall control")],
        string="Fan control type",
        tracking=True,
    )
    fan_wattage_ids = fields.One2many(
        comodel_name="lighting.product.fanwattage",
        inverse_name="product_id",
        string="Fan wattages (W)",
        copy=True,
        tracking=True,
    )
    fan_noise_level = fields.Float(
        string="Noise level (dB)",
        tracking=True,
    )
    fan_reverse_direction = fields.Selection(
        selection=YESNO,
        string="Reverse direction",
        tracking=True,
    )

    # Sources tab
    source_ids = fields.One2many(
        comodel_name="lighting.product.source",
        inverse_name="product_id",
        string="Sources",
        copy=True,
        tracking=True,
    )
    source_count = fields.Integer(
        compute="_compute_source_count", string="Total sources"
    )

    @api.depends("source_ids")
    def _compute_source_count(self):
        for rec in self:
            rec.source_count = sum(rec.source_ids.mapped("num"))

    # Beams tab
    beam_ids = fields.One2many(
        comodel_name="lighting.product.beam",
        inverse_name="product_id",
        string="Beams",
        copy=True,
        tracking=True,
    )
    beam_count = fields.Integer(
        compute="_compute_beam_count",
        string="Total beams",
    )

    @api.depends("beam_ids")
    def _compute_beam_count(self):
        for rec in self:
            rec.beam_count = sum(rec.beam_ids.mapped("num"))

    # notes tab
    note_ids = fields.One2many(
        comodel_name="lighting.product.notes",
        inverse_name="product_id",
        string="Notes",
        copy=True,
        tracking=True,
    )

    # Attachment tab
    attachment_ids = fields.One2many(
        comodel_name="lighting.attachment",
        inverse_name="product_id",
        string="Attachments",
        copy=True,
        tracking=True,
    )
    attachment_count = fields.Integer(
        compute="_compute_attachment_count", string="Attachment(s)"
    )

    @api.depends("attachment_ids")
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = self.env["lighting.attachment"].search_count(
                [("product_id", "=", record.id)]
            )

    # Optional accesories tab
    optional_ids = fields.Many2many(
        comodel_name="lighting.product",
        relation="lighting_product_optional_rel",
        column1="product_id",
        column2="optional_id",
        string="Recommended accessories",
        tracking=True,
    )
    parent_optional_accessory_product_count = fields.Integer(
        compute="_compute_parent_optional_accessory_product_count"
    )

    @api.depends("optional_ids")
    def _compute_parent_optional_accessory_product_count(self):
        for rec in self:
            rec.parent_optional_accessory_product_count = self.env[
                "lighting.product"
            ].search_count([("optional_ids", "=", rec.id)])

    is_optional_accessory = fields.Boolean(
        string="Is recommended accessory",
        compute="_compute_is_optional_accessory",
        search="_search_is_optional_accessory",
    )

    @api.depends("optional_ids")
    def _compute_is_optional_accessory(self):
        for rec in self:
            rec.is_optional_accessory = bool(
                self.env["lighting.product"].search([("optional_ids", "=", rec.id)])
            )

    def _search_is_optional_accessory(self, operator, value):
        ids = (
            self.env["lighting.product"]
            .search([("optional_ids", "!=", False)])
            .mapped("optional_ids.id")
        )
        return [("id", "in", ids)]

    # Required accessories tab
    required_ids = fields.Many2many(
        comodel_name="lighting.product",
        relation="lighting_product_required_rel",
        column1="product_id",
        column2="required_id",
        string="Mandatory accessories",
        tracking=True,
    )
    parent_required_accessory_product_count = fields.Integer(
        compute="_compute_parent_required_accessory_product_count"
    )

    @api.depends("required_ids")
    def _compute_parent_required_accessory_product_count(self):
        for record in self:
            record.parent_required_accessory_product_count = self.env[
                "lighting.product"
            ].search_count([("required_ids", "=", record.id)])

    is_required_accessory = fields.Boolean(
        compute="_compute_is_required_accessory",
        search="_search_is_required_accessory",
    )

    @api.depends("required_ids")
    def _compute_is_required_accessory(self):
        for rec in self:
            rec.is_required_accessory = bool(
                self.env["lighting.product"].search([("required_ids", "=", rec.id)])
            )

    def _search_is_required_accessory(self, operator, value):
        ids = (
            self.env["lighting.product"]
            .search([("required_ids", "!=", False)])
            .mapped("required_ids.id")
        )

        return [("id", "in", ids)]

    # Substitutes tab
    substitute_ids = fields.Many2many(
        comodel_name="lighting.product",
        relation="lighting_product_substitute_rel",
        column1="product_id",
        column2="substitute_id",
        string="Substitutes",
        tracking=True,
    )

    # logistics tab
    tariff_item = fields.Char(
        tracking=True,
    )
    assembler_id = fields.Many2one(
        comodel_name="lighting.assembler",
        ondelete="restrict",
        tracking=True,
    )
    supplier_ids = fields.One2many(
        comodel_name="lighting.product.supplier",
        inverse_name="product_id",
        string="Suppliers",
        copy=True,
        tracking=True,
    )
    ibox_weight = fields.Float(
        string="IBox weight (Kg)",
        tracking=True,
    )
    ibox_volume = fields.Float(
        string="IBox volume (cm³)",
        tracking=True,
    )
    ibox_length = fields.Float(
        string="IBox length (cm)",
        tracking=True,
    )
    ibox_width = fields.Float(
        string="IBox width (cm)",
        tracking=True,
    )
    ibox_height = fields.Float(
        string="IBox height (cm)",
        tracking=True,
    )
    mbox_qty = fields.Integer(
        string="Masterbox quantity",
        tracking=True,
    )
    mbox_weight = fields.Float(
        string="Masterbox weight (kg)",
        tracking=True,
    )
    mbox_length = fields.Float(
        string="Masterbox length (cm)",
        tracking=True,
    )
    mbox_width = fields.Float(
        string="Masterbox width (cm)",
        tracking=True,
    )
    mbox_height = fields.Float(
        string="Masterbox height (cm)",
        tracking=True,
    )

    # inventory tab
    onhand_qty = fields.Float(
        string="On hand",
        readonly=True,
        required=True,
        default=0,
        copy=False,
    )
    commited_qty = fields.Float(
        string="Commited",
        readonly=True,
        required=True,
        default=0,
        copy=False,
    )
    available_qty = fields.Float(
        string="Available",
        readonly=True,
        required=True,
        default=0,
        copy=False,
    )
    capacity_qty = fields.Float(
        string="Capacity",
        readonly=True,
        required=True,
        default=0,
        copy=False,
    )
    onorder_qty = fields.Float(
        string="On order",
        readonly=True,
        required=True,
        default=0,
        copy=False,
    )
    stock_future_qty = fields.Float(
        string="Future stock",
        readonly=True,
        required=True,
        default=0,
        copy=False,
    )
    stock_future_date = fields.Date(
        readonly=True,
        copy=False,
    )
    last_purchase_date = fields.Date(
        readonly=True,
        copy=False,
    )

    # marketing tab
    state_marketing = fields.Selection(
        selection=STATES_MARKETING,
        string="Marketing status",
        tracking=True,
    )
    on_request = fields.Boolean(
        tracking=True,
    )
    effective_date = fields.Date(
        tracking=True,
    )
    price = fields.Float(
        readonly=True,
    )
    price_currency_id = fields.Many2one(
        comodel_name="res.currency",
        readonly=True,
    )
    cost = fields.Float(
        readonly=True,
        groups="lighting.group_lighting_user",
    )
    cost_currency_id = fields.Many2one(
        comodel_name="res.currency",
        readonly=True,
        groups="lighting.group_lighting_user",
    )
    marketing_comments = fields.Char(
        string="Comments",
        tracking=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("to_review", "To review"),
            ("published", "Published"),
        ],
        string="Status",
        default="draft",
        readonly=False,
        required=True,
        copy=False,
        tracking=True,
    )

    @api.constrains("reference")
    def _check_reference_spaces(self):
        for rec in self:
            if rec.reference != rec.reference.strip():
                raise ValidationError(
                    _(
                        "The reference has trailing and/or leading spaces,"
                        " please remove them before saving."
                    )
                )

    @api.constrains("catalog_ids")
    def _check_catalog_ids(self):
        # TODO Migration Script. remove this constrain and change the catalog_ids attribute to
        # many2one
        for rec in self:
            if len(rec.catalog_ids) != 1:
                raise ValidationError(_("Only one catalog is allowed per product"))

    @api.constrains("is_composite", "required_ids")
    def _check_composite_product(self):
        for rec in self:
            if not rec.is_composite and rec.required_ids:
                raise ValidationError(
                    _(
                        "Only the composite products can have required accessories. "
                        "Enable 'is_composite' field or "
                        "remove the required accessories associated."
                    )
                )

            if rec.is_composite and not rec.required_ids:
                raise ValidationError(
                    _(
                        "You cannot have a composite product without required accessories"
                    )
                )

    @api.constrains("optional_ids", "required_ids")
    def _check_product_dependency(self):
        for rec in self:
            if rec in rec.required_ids:
                raise ValidationError(
                    _("The current reference cannot be defined as a required accessory")
                )
            if rec in rec.optional_ids:
                raise ValidationError(
                    _(
                        "The current reference cannot be defined as a recomended accessory"
                    )
                )

    # TODO: REVIEW: Self ensure
    @api.constrains("product_group_id")
    def _check_product_group(self):
        if self.product_group_id.child_ids:
            raise ValidationError(
                _(
                    "You cannot assign products to a group with childs. "
                    "The group must not have childs and be "
                    "empty or already contain products"
                )
            )

    @api.constrains("configurator", "product_group_id")
    def _check_configurator_product_group(self):
        if self.configurator and self.product_group_id:
            raise ValidationError(
                _("Products with configurator cannot belong to a group")
            )

    @api.constrains("state", "family_ids", "category_id")
    def _check_published_mandatory_fields(self):
        for rec in self:
            if rec.state == "published":
                if not rec.family_ids or not rec.category_id or not rec.location_ids:
                    raise ValidationError(
                        _(
                            "The Family, Category and Locations "
                            "are mandatory in Published state"
                        )
                    )

    def _update_with_check(self, values, key, value):
        if key not in values:
            values[key] = value
        else:
            if values[key] != value:
                raise ValidationError(
                    _(
                        "Inconsistency due to multi nature of the method, "
                        "not all records have the same values"
                    )
                )

    def _check_state_marketing_stock(self, values):
        if self:
            self.ensure_one()
        current_state = self.state_marketing
        new_state = values.get("state_marketing", current_state)
        current_state_str, new_state_str = (
            _get_state_name_map(self)[current_state],
            _get_state_name_map(self)[new_state],
        )
        new_stock = sum(
            values.get(f, self[f]) for f in ("available_qty", "stock_future_qty")
        )
        if current_state not in _get_state_name_map(self):
            raise ValidationError(_("State '%s' does not exist") % current_state_str)
        new_values = self._validate_stock_change(
            current_state, new_state, new_stock, current_state_str, new_state_str
        )
        return new_values

    def _validate_stock_change(
        self, current_state, new_state, new_stock, current_state_str, new_state_str
    ):
        new_values = {}

        if current_state in C_STATES:
            self._c_states_check(new_state, new_stock, current_state_str, new_state_str)

        elif current_state in ES_MAP:
            new_values = self._es_map_check(
                new_state,
                new_stock,
                current_state,
                current_state_str,
                new_state_str,
                new_values,
            )

        elif current_state in D_MAP:
            new_values = self._d_map_check(
                new_state,
                new_stock,
                current_state,
                current_state_str,
                new_state_str,
                new_values,
            )

        return new_values

    def _c_states_check(self, new_state, new_stock, current_state_str, new_state_str):
        if new_state in ES_MAP:
            if new_stock == 0:
                raise ValidationError(
                    _(
                        "You cannot change the state from '%(current_state)s' to "
                        "'%(new_state)s' if the product has no stock"
                    )
                    % {
                        "current_state": current_state_str,
                        "new_state": new_state_str,
                    }
                )
        elif new_state in D_MAP:
            if new_stock != 0:
                raise ValidationError(
                    _(
                        "You cannot change the state from '%(current_state)s' to "
                        "'%(new_state)s' if the product has stock (%(stock)g)"
                    )
                    % {
                        "current_state": current_state_str,
                        "new_state": new_state_str,
                        "stock": new_stock,
                    }
                )
        elif new_state in C_STATES:
            pass
        else:
            raise ValidationError(
                _("Transition from '%(current_state)s' to '%(new_state)s' not allowed")
                % {
                    "current_state": current_state_str,
                    "new_state": new_state_str,
                }
            )

    def _es_map_check(
        self,
        new_state,
        new_stock,
        current_state,
        current_state_str,
        new_state_str,
        new_values,
    ):
        if new_state in C_STATES:
            if new_state and new_stock == 0:
                raise ValidationError(
                    _(
                        "You cannot change the state from '%(current_state)s' to "
                        "'%(new_state)s' if the product has no stock"
                    )
                    % {
                        "current_state": current_state_str,
                        "new_state": new_state_str,
                    }
                )
        elif new_state == ES_MAP[current_state]:
            if new_stock != 0:
                raise ValidationError(
                    _(
                        "You cannot change the state from '%(current_state)s' to "
                        "'%(new_state)s' if the product has stock (%(stock)g)"
                    )
                    % {
                        "current_state": current_state_str,
                        "new_state": new_state_str,
                        "stock": new_stock,
                    }
                )
        elif new_state == current_state:
            if new_stock == 0:
                self._update_with_check(
                    new_values, "state_marketing", ES_MAP[current_state]
                )
        elif new_state in ES_MAP:
            pass
        elif not new_state:
            pass
        else:
            raise ValidationError(
                _("Transition from '%(current_state)s' to '%(new_state)s' not allowed")
                % {
                    "current_state": current_state_str,
                    "new_state": new_state_str,
                }
            )
        return new_values

    def _d_map_check(
        self,
        new_state,
        new_stock,
        current_state,
        current_state_str,
        new_state_str,
        new_values,
    ):
        if new_state in C_STATES:
            pass
        elif new_state == D_MAP[current_state]:
            if new_stock == 0:
                raise ValidationError(
                    _(
                        "You cannot change the state from '%(current_state)s' to "
                        "'%(new_state)s' if the product has no stock"
                    )
                    % {
                        "current_state": current_state_str,
                        "new_state": new_state_str,
                    }
                )
        elif new_state == current_state:
            if new_stock != 0:
                self._update_with_check(
                    new_values, "state_marketing", D_MAP[current_state]
                )
        elif new_state in D_MAP:
            pass
        elif not new_state:
            pass
        else:
            raise ValidationError(
                _(
                    "Transition from '%(current_state)s' to "
                    "'%(new_state)s' not allowed"
                )
                % {
                    "current_state": current_state_str,
                    "new_state": new_state_str,
                }
            )
        return new_values

    def copy(self, default=None):
        self.ensure_one()

        # generate non duplicated new reference
        reference_tmp = self.reference
        while True:
            product_ids = self.env[self._name].search(
                [("reference", "=", reference_tmp)]
            )
            if len(product_ids) == 0:
                break
            reference_tmp = "%s (copy)" % reference_tmp

        default = dict(
            default or {},
            reference=reference_tmp,
            ean=False,
        )

        return super().copy(default)

    def write(self, values):
        if "reference" in values and "default_code" not in values:
            values["default_code"] = values["reference"]
        if "price" in values and "lst_price" not in values:
            values["lst_price"] = values["price"]
        result = True
        for rec in self:
            new_values = rec._check_state_marketing_stock(values)
            if new_values:
                values.update(new_values)
            original_description = rec.description
            result &= super(LightingProduct, rec).write(values)
            if rec.description != original_description:
                for lang in self.env["res.lang"].search([]):
                    rec = rec.with_context(lang=lang.code)
                    rec.name = (
                        rec.description or rec.description_manual or rec.reference
                    )
        return result

    # TODO: remove comented code if it works
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update(
                {
                    "name": vals["reference"],
                    "default_code": vals["reference"],
                    "lst_price": 0,
                }
            )
            new_values = self._check_state_marketing_stock(vals)
            if new_values:
                vals.update(new_values)
        res = super().create(vals_list)
        for rec in res:
            # TODO: Change name for all languages
            description = res.description or res.description_manual
            if description:
                if rec.name != description:
                    rec.name = description
        return res

    def unlink(self):
        product_tmpl = self.mapped("odoop_id.product_tmpl_id")
        res = super().unlink()
        res &= product_tmpl.unlink()
        return res
