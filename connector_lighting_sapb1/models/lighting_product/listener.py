# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class SAPB1LightingProductImporter(Component):
    _name = "sapb1.lighting.product.listener"
    _inherit = "sapb1.lighting.listener"

    _apply_on = "lighting.product"

    def on_record_write(self, record, fields=None):
        export_only_fields = {
            "category_id",
            "family_ids",
            "state_marketing",
            "catalog_ids",
            "configurator",
        }
        if "state" in fields:
            if record.state == "published":
                export_only_fields.add("state")
        import_export_fields = set()
        export = False
        if fields is None or export_only_fields & set(fields):
            export = True
        else:
            if not self.env.context.get("connector_no_export", False):
                export = import_export_fields & set(fields)
        if export:
            for backend in record.sudo().sapb1_lighting_bind_ids.mapped("backend_id"):
                self.env["sapb1.lighting.product"].sudo(
                    backend.user_id
                ).with_delay().export_record(backend.sudo(backend.user_id), record)
