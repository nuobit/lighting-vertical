# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


def float2text(f, decs=2):
    if f == int(f):
        return "%i" % int(f)
    else:
        return ("{0:.%if}" % decs).format(f)


class LightingProductSourceLine(models.Model):
    _name = "lighting.product.source.line"
    _description = "Product Source Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "type_id"
    _order = "sequence"

    sequence = fields.Integer(
        required=True,
        default=1,
        help="The sequence field is used to define order",
    )
    type_id = fields.Many2one(
        comodel_name="lighting.product.source.type",
        ondelete="restrict",
        string="Type",
        required=True,
    )
    wattage = fields.Float()
    is_max_wattage = fields.Boolean(
        string="Is max. Wattage",
    )
    wattage_magnitude = fields.Selection(
        selection=[("w", "W"), ("wm", "W/m")],
        string="Wattage magnitude",
        default="w",
    )

    @api.constrains("wattage", "type_id", "is_integrated")
    def _check_wattage(self):
        for rec in self:
            if rec.type_id.is_integrated and rec.wattage <= 0:
                raise ValidationError(
                    _(
                        "%(source_id)s: The wattage on line %type_id must be greater "
                        "than 0 if source type is integrated"
                    )
                    % {
                        "source_id": rec.source_id.product_id.display_name,
                        "type_id": rec.type_id.display_name,
                    }
                )

    color_temperature_flux_ids = fields.One2many(
        string="Color temperature/Flux",
        comodel_name="lighting.product.source.line.color.temperature.flux",
        inverse_name="source_line_id",
        copy=True,
    )
    is_color_temperature_flux_tunable = fields.Boolean(
        string="Tunable",
        default=False,
    )

    # TODO: Modify this onchange
    @api.onchange("color_temperature_flux_ids", "is_color_temperature_flux_tunable")
    def _onchange_is_color_temperature_flux_ids_tunable(self):
        if len(self.color_temperature_flux_ids) > 2:
            if self.is_color_temperature_flux_tunable:
                color_temp_fluxs_ord = self.color_temperature_flux_ids.sorted(
                    lambda x: x.color_temperature_id.value
                )
                self.color_temperature_flux_ids = [
                    (
                        6,
                        False,
                        (color_temp_fluxs_ord[0] | color_temp_fluxs_ord[-1]).mapped(
                            "id"
                        ),
                    )
                ]
        elif len(self.color_temperature_flux_ids) < 2:
            if self.is_color_temperature_flux_tunable:
                self.is_color_temperature_flux_tunable = False

    color_temperature_display = fields.Char(
        string="Color temperature",
        compute="_compute_color_temperature_flux_display",
    )
    luminous_flux_display = fields.Char(
        string="Luminous flux",
        compute="_compute_color_temperature_flux_display",
    )
    energy_efficiency_display = fields.Char(
        string="Energy Efficiency",
        compute="_compute_color_temperature_flux_display",
    )

    # TODO: Split this compute?
    @api.depends(
        "color_temperature_flux_ids",
        "color_temperature_flux_ids.color_temperature_id",
        "color_temperature_flux_ids.color_temperature_id.value",
        "color_temperature_flux_ids.nominal_flux",
        "color_temperature_flux_ids.flux_magnitude",
        "color_temperature_flux_ids.efficiency_id",
        "color_temperature_flux_ids.efficiency_id.name",
        "is_color_temperature_flux_tunable",
        "source_id",
    )
    def _compute_color_temperature_flux_display(self):
        for rec in self:
            if rec.color_temperature_flux_ids:
                # compute color_temperature_display
                if (
                    len(rec.color_temperature_flux_ids) != 1
                    or rec.color_temperature_flux_ids.color_temperature_id.value
                ):
                    color_temperature_values = rec.color_temperature_flux_ids.filtered(
                        lambda x: not self.env.context.get("ignore_nulls")
                        or x.color_temperature_id.value
                    ).sorted(lambda x: x.color_temperature_id.value)
                    rec.color_temperature_display = (
                        rec.is_color_temperature_flux_tunable and "-" or "/"
                    ).join(
                        [
                            x.color_temperature_id.value
                            and ("%iK" % x.color_temperature_id.value)
                            or "-"
                            for x in color_temperature_values
                        ]
                    )
                else:
                    rec.color_temperature_display = False
                # compute luminous_flux_display
                flux_magnitude_options = dict(
                    rec.color_temperature_flux_ids.fields_get(
                        ["flux_magnitude"], ["selection"]
                    )
                    .get("flux_magnitude")
                    .get("selection")
                )
                separator = rec.is_color_temperature_flux_tunable and "-" or "/"
                ctf_l = []
                for ctf in rec.color_temperature_flux_ids.sorted(
                    lambda x: x.color_temperature_id.value
                ):
                    f_l = []
                    if not self.env.context.get("ignore_nulls") or ctf.nominal_flux:
                        f_l.append(
                            "%g%s"
                            % (
                                ctf.nominal_flux,
                                flux_magnitude_options[ctf.flux_magnitude],
                            )
                        )
                    else:
                        f_l.append("-")
                    if ctf.total_flux:
                        f_l.append(
                            "(%g%s)"
                            % (
                                ctf.total_flux,
                                flux_magnitude_options[ctf.flux_magnitude],
                            )
                        )
                    ctf_l.append("".join(f_l))
                rec.luminous_flux_display = separator.join(ctf_l)
                # compute energy_efficiency_display
                if rec.color_temperature_flux_ids.mapped("efficiency_id"):
                    if (
                        len(rec.color_temperature_flux_ids) != 1
                        or rec.color_temperature_flux_ids.efficiency_id.name
                    ):
                        energy_efficiency_values = (
                            rec.color_temperature_flux_ids.filtered(
                                lambda x: not self.env.context.get("ignore_nulls")
                                or x.efficiency_id.name
                            ).sorted(lambda x: x.efficiency_id.sequence)
                        )
                        rec.energy_efficiency_display = (
                            rec.is_color_temperature_flux_tunable and "-" or "/"
                        ).join(
                            [
                                x.efficiency_id.name
                                and ("%s" % x.efficiency_id.name)
                                or "-"
                                for x in energy_efficiency_values
                            ]
                        )
                else:
                    if rec.efficiency_ids:
                        energy_efficiency_values = rec.efficiency_ids.filtered(
                            lambda x: not self.env.context.get("ignore_nulls") or x.name
                        ).sorted(lambda x: x.sequence)
                        rec.energy_efficiency_display = "/".join(
                            energy_efficiency_values.mapped("name")
                        )
                    else:
                        rec.energy_efficiency_display = False
            else:
                rec.energy_efficiency_display = False
                rec.color_temperature_display = False
                rec.luminous_flux_display = False

    # TODO: This to remove is an old comment.
    # to remove
    color_temperature_ids = fields.Many2many(
        string="Color temperature",
        comodel_name="lighting.product.color.temperature",
        relation="lighting_product_source_line_color_temperature_rel",
        column1="source_line_id",
        column2="color_temperature_id",
    )
    is_color_temperature_tunable = fields.Boolean(
        string="Tunableold",
        default=False,
    )
    luminous_flux1 = fields.Integer(
        string="Luminous flux 1 (lm)",
    )
    luminous_flux2 = fields.Integer(
        string="Luminous flux 2 (lm)",
    )

    cri_min = fields.Integer(
        string="CRI",
        help="Minimum color rendering index",
        tracking=True,
    )
    is_led = fields.Boolean(
        related="type_id.is_led",
        readonly=False,
    )
    color_consistency = fields.Float(
        string="Color consistency (SDCM)",
    )
    special_spectrum_id = fields.Many2one(
        comodel_name="lighting.product.special.spectrum",
        string="Special spectrum",
    )
    leds_m = fields.Integer(
        string="Leds/m",
        tracking=True,
    )
    led_chip_ids = fields.One2many(
        comodel_name="lighting.product.ledchip",
        inverse_name="source_line_id",
        string="Chip",
        copy=True,
    )
    efficiency_ids = fields.Many2many(
        comodel_name="lighting.energyefficiency",
        relation="lighting_product_source_energyefficiency_rel",
        string="Energy efficiency",
    )
    # # do not use a related here, keep it computed at least in v11
    # is_integrated = fields.Boolean(
    #     compute="_compute_is_integrated",
    #     store=True,
    # )
    # TODO: Why this compute can't be a related? try it!
    is_integrated = fields.Boolean(
        related="type_id.is_integrated",
        store=True,
    )

    # @api.depends("type_id.is_integrated")
    # def _compute_is_integrated(self):
    #     for rec in self:
    #         rec.is_integrated = rec.type_id.is_integrated

    is_lamp_included = fields.Boolean(
        string="Lamp included?",
        compute="_compute_is_lamp_included",
        store=True,
        readonly=False,
    )

    # TODO:Check if this compute works as the previous onchange
    @api.depends("type_id.is_integrated", "is_lamp_included")
    def _compute_is_lamp_included(self):
        for rec in self:
            if rec.type_id.is_integrated and rec.is_lamp_included:
                rec.is_lamp_included = False

    # @api.onchange("type_id", "is_integrated")
    # def _onchange_type_id(self):
    #     if self.type_id.is_integrated and self.is_lamp_included:
    #         self.is_lamp_included = False

    def write(self, vals):
        for rec in self:
            # deal with the color temperature fluxes
            # if the source is or is not integrated/lamp included
            color_temperature_flux_ids = vals.get(
                "color_temperature_flux_ids", rec.color_temperature_flux_ids
            )
            if color_temperature_flux_ids:
                if "type_id" in vals:
                    source_type = self.env["lighting.product.source.type"].browse(
                        vals["type_id"]
                    )
                    is_integrated = source_type.is_integrated
                else:
                    is_integrated = vals.get("is_integrated", rec.is_integrated)
                is_lamp_included = vals.get("is_lamp_included", rec.is_lamp_included)
                if not (is_integrated or is_lamp_included):
                    vals["color_temperature_flux_ids"] = [(5, 0, 0)]
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # deal with the color temperature fluxes
            # if the source is or is not integrated/lamp included
            if "color_temperature_flux_ids" in vals:
                if "is_integrated" not in vals:
                    if "type_id" not in vals:
                        raise ValidationError(_("The source type is not defined"))
                    source_type = self.env["lighting.product.source.type"].browse(
                        vals["type_id"]
                    )
                    vals["is_integrated"] = source_type.is_integrated
                is_integrated = vals["is_integrated"]
                is_lamp_included = vals.get("is_lamp_included", False)
                if not (is_integrated or is_lamp_included):
                    del vals["color_temperature_flux_ids"]
        return super().create(vals_list)

    # computed fields
    wattage_display = fields.Char(
        compute="_compute_wattage_display",
        string="Wattage (W)",
    )

    def prepare_wattage_str(self, mult=1, is_max_wattage=None):
        self.ensure_one()

        if is_max_wattage is None:
            is_max_wattage = self.is_max_wattage

        wattage_magnitude_option = dict(
            self.fields_get(["wattage_magnitude"], ["selection"])
            .get("wattage_magnitude")
            .get("selection")
        )

        res = []
        if self.wattage > 0:
            wattage_str = float2text(self.wattage)
            if mult > 1:
                wattage_str = "%ix%s" % (mult, wattage_str)

            if self.wattage_magnitude:
                wattage_str += wattage_magnitude_option.get(self.wattage_magnitude)
            res.append(wattage_str)

        if is_max_wattage:
            res.append(_("max."))

        if res != []:
            return " ".join(res)
        else:
            return False

    @api.depends("wattage", "is_max_wattage", "wattage_magnitude")
    def _compute_wattage_display(self):
        for rec in self:
            rec.wattage_display = rec.prepare_wattage_str()

    source_id = fields.Many2one(
        comodel_name="lighting.product.source",
        ondelete="cascade",
        string="Source",
    )

    @api.constrains("type_id", "is_integrated", "is_lamp_included")
    def _check_integrated_vs_lamp_included(self):
        for rec in self:
            if rec.type_id.is_integrated and rec.is_lamp_included:
                raise ValidationError(
                    _(
                        "An integrated type is not compatible "
                        "with having lamp included. Product %s."
                        "Please select either a integrated type "
                        "or lamp included but not both."
                    )
                    % rec.source_id.product_id.reference
                )

    @api.constrains("efficiency_ids", "type_id", "is_integrated", "is_lamp_included")
    def _check_efficiency_integrated_lamp_included(self):
        for rec in self:
            if (
                rec.efficiency_ids
                and not rec.type_id.is_integrated
                and not rec.is_lamp_included
            ):
                raise ValidationError(
                    _(
                        "You cannot inform the Efficiency Energy if the source "
                        "is not integrated and the lamp is not included."
                        "\nProducts affected: %s."
                    )
                    % rec.source_id.product_id.reference
                )

    @api.constrains("color_temperature_flux_ids", "is_color_temperature_flux_tunable")
    def _check_color_temperature_flux_ids_tunable(self):
        for rec in self:
            if (
                rec.is_color_temperature_flux_tunable
                and rec.color_temperature_flux_ids
                and len(rec.color_temperature_flux_ids) != 2
            ):
                raise ValidationError(
                    _(
                        "A tunable source must have exactly "
                        "2 pairs color temperature/luminous flux"
                    )
                )

    @api.constrains("efficiency_ids", "color_temperature_flux_ids")
    def _check_efficiencies(self):
        for rec in self:
            if (
                rec.color_temperature_flux_ids.mapped("efficiency_id")
                and rec.efficiency_ids
            ):
                raise ValidationError(_("Efficiency must be defined only in CCT table"))

    @api.constrains("source_id", "is_integrated")
    def _check_integrated_vs_lampholder(self):
        for rec in self:
            if (
                rec.source_id.lampholder_id or rec.source_id.lampholder_technical_id
            ) and rec.type_id.is_integrated:
                raise ValidationError(_("An integrated source cannot have lampholder"))

    @api.constrains("efficiency_ids")
    def _check_efficiency_lampholder(self):
        for rec in self:
            if all(
                [
                    rec.source_id.lampholder_id
                    or rec.source_id.lampholder_technical_id,
                    rec.efficiency_ids,
                    not rec.source_id.product_id.is_accessory,
                ]
            ):
                raise ValidationError(
                    _("A non accessory source with lampholder cannot have efficiency")
                )

    # TODO: the follow functions are so similar. Refactor?
    # aux display fucnitons
    def get_source_type(self):
        res = self.sorted(lambda x: x.sequence).mapped("type_id.display_name")
        if not res:
            return None
        return res

    def get_color_temperature(self):
        res = (
            self.filtered(lambda x: x.color_temperature_flux_ids)
            .filtered(lambda x: x.color_temperature_display)
            .sorted(lambda x: x.sequence)
            .mapped("color_temperature_display")
        )
        if not res:
            return None
        return res

    def get_luminous_flux(self):
        res = (
            self.filtered(lambda x: x.color_temperature_flux_ids)
            .filtered(lambda x: x.luminous_flux_display)
            .sorted(lambda x: x.sequence)
            .mapped("luminous_flux_display")
        )
        if not res:
            return None
        return res

    def get_energy_efficiency(self):
        res = (
            self.filtered(lambda x: x.energy_efficiency_display)
            .sorted(lambda x: x.sequence)
            .mapped("energy_efficiency_display")
        )
        if not res:
            return None
        return res

    def get_special_spectrum(self):
        res = (
            self.filtered(lambda x: x.special_spectrum_id)
            .sorted(lambda x: x.sequence)
            .mapped("special_spectrum_id.name")
        )
        if not res:
            return None
        return res

    def get_cri(self):
        res = (
            self.sorted(lambda x: x.sequence)
            .filtered(lambda x: x.cri_min)
            .mapped("cri_min")
        )
        if not res:
            return None
        return res

    def get_leds_m(self):
        res = (
            self.sorted(lambda x: x.sequence)
            .filtered(lambda x: x.leds_m)
            .mapped("leds_m")
        )
        if not res:
            return None
        return res

    def get_wattage(self):
        w_d = {}
        for rec in self:
            if rec.wattage:
                if rec.wattage_magnitude not in w_d:
                    w_d[rec.wattage_magnitude] = []
                w_d[rec.wattage_magnitude].append((rec.wattage, rec.is_max_wattage))

        if not w_d:
            return None

        wattage_magnitude_option = dict(
            self.fields_get(["wattage_magnitude"], ["selection"])
            .get("wattage_magnitude")
            .get("selection")
        )

        w_l = []
        for wm, wvm_l in w_d.items():
            ws = wattage_magnitude_option.get(wm)
            wt = None
            if len(wvm_l) == 1:
                wattage, is_max_wattage = wvm_l[0]
                wt = "%g%s" % (wattage, ws)
                if is_max_wattage:
                    wt = "%s %s" % (wt, _("max."))
            elif len(wvm_l) > 1:
                wv_l = [x[0] for x in wvm_l]
                wt = "%g%s %s" % (max(wv_l), ws, _("max."))
            if wt:
                w_l.append(wt)
        if not w_l:
            return None
        return "/".join(w_l)
