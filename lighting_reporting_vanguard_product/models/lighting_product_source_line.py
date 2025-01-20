# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class LightingProductSourceLine(models.Model):
    _inherit = "lighting.product.source.line"

    def _prepend_source_num(self, value):
        self.ensure_one()
        values_l = []
        if self.source_id.num > 1:
            values_l.append("(%ix)" % self.source_id.num)
        values_l.append(value)
        return "".join(values_l)

    def _get_color_temperature_flux_values(self, flux_attr):
        self.ensure_one()
        found = False
        flux_data = []
        for flux in self.color_temperature_flux_ids:
            value = flux[flux_attr]
            if value:
                value = self.get_format_lang_decimal(value) + flux.flux_magnitude
                if not found:
                    found = True
            else:
                value = "-"
            flux_data.append(value)
        return found and "/".join(flux_data)

    def get_nominal_flux_display(self):
        self.ensure_one()
        return self._prepend_source_num(
            self._get_color_temperature_flux_values("nominal_flux")
        )

    def get_total_flux_display(self):
        self.ensure_one()
        return self._prepend_source_num(
            self._get_color_temperature_flux_values("total_flux")
        )

    def get_total_wattage_display(self):
        self.ensure_one()
        wattage_magnitude_map = dict(
            self.fields_get("wattage_magnitude")["wattage_magnitude"]["selection"]
        )
        value = [
            self.get_format_lang_decimal(self.wattage),
            wattage_magnitude_map[self.wattage_magnitude],
        ]
        return self._prepend_source_num(" ".join(value))

    def get_color_consistency_display(self):
        self.ensure_one()
        return self.get_format_lang_decimal(self.color_consistency)
