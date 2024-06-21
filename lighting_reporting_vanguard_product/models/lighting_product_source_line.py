# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class LightingProductSourceLine(models.Model):
    _inherit = "lighting.product.source.line"

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
        return self._get_color_temperature_flux_values("nominal_flux")

    def get_total_flux_display(self):
        self.ensure_one()
        return self._get_color_temperature_flux_values("total_flux")

    def get_color_consistency_display(self):
        self.ensure_one()
        return self.get_format_lang_decimal(self.color_consistency)
