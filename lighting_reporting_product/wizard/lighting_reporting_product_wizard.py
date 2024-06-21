# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class LightingReportingProductWizard(models.TransientModel):
    _name = "lighting.reporting.product.wizard"

    @api.model
    def default_get(self, fields_list):
        rec = super().default_get(fields_list)
        lang = self.env.context.get("lang")
        if lang:
            rec["lang_id"] = self.env["res.lang"].search([("code", "=", lang)]).id
        product_template = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("lighting_reporting_product.product_template")
        )
        if product_template in dict(self._fields["template"].selection):
            rec["template"] = product_template
        rec["template_visible"] = bool(self._fields["template"].selection)
        return rec

    lang_id = fields.Many2one(
        string="Language",
        comodel_name="res.lang",
        required=True,
    )
    template = fields.Selection(selection=[], invisible=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        required=True,
        domain="[('id', 'in', allowed_company_ids)]",
    )
    template_visible = fields.Boolean()

    def print_product_datasheet(self):
        """Print the product datasheet."""
        return NotImplementedError
