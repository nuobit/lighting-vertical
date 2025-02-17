# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models


class LightingCatalog(models.Model):
    _inherit = "lighting.catalog"

    def action_export_bmecat(self):
        self.ensure_one()
        return {
            "name": _("BMEcat Catalog"),
            "type": "ir.actions.act_window",
            "res_model": "lighting.export.bmecat",
            "view_mode": "form",
            "view_id": self.env.ref(
                "lighting_export_bmecat.lighting_export_bmecat_view_form"
            ).id,
            "target": "current",
            "context": {"default_catalog_id": self.id},
        }
