# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class LightingProductSource(models.Model):
    _inherit = "lighting.product.source"

    def get_energy_efficiency(self):
        ccts_by_ef = {}
        cct_flux = self.mapped("line_ids.color_temperature_flux_ids").sorted(
            lambda x: (x.efficiency_id.sequence, x.color_temperature_id.value)
        )
        if cct_flux.mapped("efficiency_id"):
            for line in cct_flux:
                if line.efficiency_id:
                    ccts_by_ef.setdefault(
                        line.efficiency_id, self.env[line.color_temperature_id._name]
                    )
                    ccts_by_ef[line.efficiency_id] |= line.color_temperature_id
        else:
            for efficiency in self.mapped("line_ids.efficiency_ids"):
                ccts_by_ef[efficiency] = cct_flux.mapped("color_temperature_id")
        return ccts_by_ef

    @api.model
    def energy_efficiency_display(self, ccts_by_ef):
        efs = []
        for efficiency, ccts in ccts_by_ef.items():
            efs_l = [efficiency.name]
            if ccts:
                efs_l.append("(%s)" % ", ".join([x.display_name for x in ccts]))
            efs.append(" ".join(efs_l))
        return ", ".join(efs)
