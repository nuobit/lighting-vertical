# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models


class LightingExport(models.TransientModel):
    _inherit = "lighting.export"

    output_type = fields.Selection(
        selection_add=[("export_product_json", _("Json file (.json)"))],
        ondelete={"export_product_json": "cascade"},
    )
    pretty_print = fields.Boolean(
        default=True,
    )
    sort_keys = fields.Boolean(
        help="If sort_keys is true (default: False), then the "
        "output of dictionaries will be sorted by key.",
        default=True,
    )

    def export_product_json(self):
        self.ensure_one()
        return {
            "type": "ir.actions.report",
            "report_name": "lighting_export_json.export_product_json",
            "report_type": "json",
            "data": {
                "interval": self.interval,
                "hide_empty_fields": self.hide_empty_fields,
                "pretty_print": self.pretty_print,
                "template_id": self.template_id.id,
                "active_ids": self.env.context.get("active_ids"),
                "lang": self.lang_id.code,
            },
        }
