# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models


class LightingExport(models.TransientModel):
    _name = "lighting.export"
    _description = "Export data"

    template_id = fields.Many2one(
        comodel_name="lighting.export.template",
        ondelete="cascade",
        required=True,
    )
    interval = fields.Selection(
        selection=[("all", _("All")), ("selection", _("Selection"))],
        default="selection",
    )
    hide_empty_fields = fields.Boolean(
        default=True,
    )
    lang_id = fields.Many2one(
        comodel_name="res.lang",
        required=True,
    )
    output_type = fields.Selection(
        selection=[],
        required=True,
    )
    exclude_configurator = fields.Boolean()

    def export_product(self):
        self.ensure_one()
        # TODO:Modify this getattr
        return getattr(self, self.output_type)()
