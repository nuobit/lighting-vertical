# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LightingProductSource(models.Model):
    _name = "lighting.product.source"
    _description = "Product Source"
    _rec_name = "relevance"
    _order = "sequence"

    sequence = fields.Integer(
        required=True,
        default=1,
        help="The sequence field is used to define order",
    )
    relevance = fields.Selection(
        selection=[("main", "Main"), ("aux", "Auxiliary")],
        required=True,
        default="main",
    )
    num = fields.Integer(
        string="Number of sources",
        default=1,
    )
    lampholder_id = fields.Many2one(
        comodel_name="lighting.product.source.lampholder",
        ondelete="restrict",
    )
    lampholder_technical_id = fields.Many2one(
        comodel_name="lighting.product.source.lampholder",
        ondelete="restrict",
        string="Technical lampholder",
    )
    line_ids = fields.One2many(
        comodel_name="lighting.product.source.line",
        inverse_name="source_id",
        string="Lines",
        copy=True,
    )
    product_id = fields.Many2one(
        comodel_name="lighting.product",
        ondelete="cascade",
    )

    # computed fields
    line_display = fields.Char(
        compute="_compute_line_display",
        string="Description",
    )

    @api.depends("line_ids")
    def _compute_line_display(self):
        for rec in self:
            res = []
            for line in rec.line_ids.sorted(lambda x: x.sequence):
                name = [line.type_id.code]

                if line.is_integrated or line.is_lamp_included:
                    if line.color_temperature_flux_ids:
                        if line.color_temperature_display:
                            name.append(line.color_temperature_display)
                        if line.luminous_flux_display:
                            name.append(line.luminous_flux_display)
                    if line.is_led and line.cri_min:
                        name.append("CRI%i" % line.cri_min)
                    if line.is_led and line.leds_m:
                        name.append("%i Leds/m" % line.leds_m)
                    if line.is_led and line.special_spectrum_id:
                        name.append(line.special_spectrum_id.name)

                if line.wattage_display:
                    name.append("(%s)" % line.wattage_display)
                res.append(" ".join(name))
            if res != []:
                rec.line_display = " / ".join(res)
            else:
                rec.line_display = False

    @api.constrains("lampholder_id", "lampholder_technical_id", "line_ids")
    def _check_efficiency_lampholder(self):
        for rec in self:
            if all(
                [
                    rec.lampholder_id or rec.lampholder_technical_id,
                    rec.line_ids.mapped("efficiency_ids"),
                    not rec.product_id.is_accessory,
                ]
            ):
                raise ValidationError(
                    _("A non accessory source with lampholder cannot have efficiency")
                )

    # TODO: The follow functions has a lot of code duplicated, can we do a generic function?
    # aux display functions
    def get_source_type(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            s = []
            if src.lampholder_id:
                s.append(src.lampholder_id.display_name)

            src_t = src.line_ids.get_source_type()
            if src_t:
                s.append("/".join(src_t))

            s_l = None
            if s:
                s_l = " ".join(s)
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
                k_l = ",".join(src_k)
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
                    kn_l.append("%ix" % src.num)
                kn_l.append(",".join(src_k))
                k_l = " ".join(kn_l)
            res.append(k_l)
        if not any(res):
            return None
        return res

    def get_cri(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            src_k = src.line_ids.get_cri()
            if src_k:
                k_l = ",".join(["CRI%i" % x for x in src_k])
                res.append(k_l)
        if not any(res):
            return None
        return res

    def get_leds_m(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            src_k = src.line_ids.get_leds_m()
            if src_k:
                k_l = ",".join([str(x) for x in src_k])
                res.append("%s Leds/m" % (k_l,))
        if not any(res):
            return None
        return res

    def get_special_spectrum(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            src_k = src.line_ids.get_special_spectrum()
            if src_k:
                k_l = ",".join(src_k)
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
                    kn_l.append("%ix" % src.num)
                kn_l.append(src_k)
                res.append(" ".join(kn_l))
        if not any(res):
            return None
        return res
