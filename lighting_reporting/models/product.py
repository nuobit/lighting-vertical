# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


def chunks(li, n):
    if not li:
        return
    yield li[:n]
    yield from chunks(li[n:], n)


class LightingProduct(models.Model):
    _inherit = "lighting.product"

    datasheet_generation_date = fields.Datetime(
        compute="_compute_datasheet_generation_date"
    )

    def _compute_datasheet_generation_date(self):
        for rec in self:
            rec.datasheet_generation_date = fields.Datetime.now()

    def product_datasheet_wizard(self):
        action = self.env.ref(
            "lighting_reporting.product_datasheet_wizard_action"
        ).read()[0]
        return action

    def get_sheet_sources(self):
        res = []
        for source in self.source_ids.sorted(lambda x: x.sequence):
            source_res = []
            source_type = source.get_source_type()
            if source_type:
                source_res.append(source_type[0])
            source_wattage = source.get_wattage()
            if source_wattage:
                source_res.append(source_wattage[0])
            source_flux = source.get_luminous_flux()
            if source_flux:
                source_res.append(source_flux[0])
            source_temp = source.get_color_temperature()
            if source_temp:
                source_res.append(source_temp[0])
            source_cri = source.get_cri()
            if source_cri:
                source_res.append(source_cri[0])
            source_leds_m = source.get_leds_m()
            if source_leds_m:
                source_res.append(source_leds_m[0])
            source_spectrum = source.get_special_spectrum()
            if source_spectrum:
                source_res.append(source_spectrum[0].upper())
            if source_res:
                res.append(" ".join(source_res))
        return res

    def get_sheet_beams(self):
        res = []
        for beam in self.beam_ids:
            beam_res = []
            s_angle = beam.get_beam_angle()
            if s_angle:
                beam_res.append(s_angle[0])
            s_phm = beam.get_beam_photometric_distribution()
            if s_phm:
                beam_res.append(s_phm[0])
            if beam_res:
                res.append(" - ".join(beam_res))
        return res

    def get_is_lamp_included(self):
        line_ids = self.source_ids.mapped("line_ids")
        integrated_line_ids = line_ids.filtered(lambda x: x.is_integrated)
        lamp_included_line_ids = line_ids.filtered(
            lambda x: not x.is_integrated
        ).mapped("is_lamp_included")
        if integrated_line_ids:
            return any(lamp_included_line_ids) or None
        else:
            return any(lamp_included_line_ids)

    def filter_by_catalogued(self):
        return self.filtered(lambda x: x.state_marketing in ("N", "C", "ES"))

    def get_usb(self):
        self.ensure_one()
        res = []
        if self.usb_ports:
            res.append("(%g)" % self.usb_ports)
        res_usbv = []
        if self.usb_voltage:
            res_usbv.append("%gV" % self.usb_voltage)
        if self.usb_current:
            res_usbv.append("%gmA" % self.usb_current)
        if res_usbv:
            res.append(" ".join(res_usbv))

        if res:
            return " x ".join(res)

        return None

    def get_operating_temperature_range(self):
        res = []
        if self.operating_temperature_min:
            res.append("%i" % self.operating_temperature_min)
        if self.operating_temperature_max:
            res.append("%i" % self.operating_temperature_max)

        if res:
            return "%s ºC" % " - ".join(res)

        return None

    def get_datasheet_url(self):
        self.ensure_one()
        url = "{}/web/datasheet/{}/{}".format(
            self.env["ir.config_parameter"].sudo().get_param("web.base.url"),
            self.env.context.get("lang"),
            self.reference,
        )
        return url

    def get_attachments_by_type(self, atype, only_images=True):
        attachments = self.env["lighting.attachment"]
        for rec in self:
            attachments |= rec.attachment_ids.filtered(
                lambda x: x.type_id.code == atype and (not only_images or x.image_known)
            ).sorted(lambda x: (x.sequence, x.id))

        return attachments

    def get_complementary_fp_images(self, groupsof=None):
        # FP's current product
        attachments = self.get_attachments_by_type("FP")

        if not groupsof:
            groupsof = len(attachments)

        return list(chunks(attachments, groupsof))

    def get_complementary_fa_images(self, groupsof=None):
        # FA's current product
        attachments = self.get_attachments_by_type("FA")[2:]

        if not groupsof:
            groupsof = len(attachments)

        return list(chunks(attachments, groupsof))

    def get_groups_same_family(self, groupsof=None):
        groups = (
            self.search(
                [
                    ("id", "!=", self.id),
                    ("family_ids", "in", self.family_ids.mapped("id")),
                ]
            )
            .mapped("product_group_id")
            .get_parent_group_by_type("PHOTO")
            .filtered(
                lambda x: self not in x.flat_product_ids
                and x.flat_product_ids.filter_by_catalogued()
                and not all(x.flat_category_ids.mapped("root_id.is_accessory"))
            )
            .sorted(lambda x: x.name)
        )

        if not groupsof:
            groupsof = len(groups)

        return list(chunks(groups, groupsof))
