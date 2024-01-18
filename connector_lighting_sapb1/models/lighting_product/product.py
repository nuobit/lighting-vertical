# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LightingProduct(models.Model):
    _inherit = "lighting.product"

    sapb1_lighting_bind_ids = fields.One2many(
        comodel_name="lighting.sapb1.product",
        inverse_name="odoo_id",
        string="SAP B1 Bindings",
    )
    sapb1_write_date = fields.Datetime(
        compute="_compute_sapb1_write_date",
        store=True,
        required=True,
        default=fields.Datetime.now,
    )

    @api.depends(
        "category_id", "family_ids", "state_marketing", "catalog_ids", "configurator"
    )
    def _compute_sapb1_write_date(self):
        for rec in self:
            rec.sapb1_write_date = fields.Datetime.now()

    @api.constrains("reference")
    def _check_reference(self):
        for rec in self:
            if rec.sudo().sapb1_lighting_bind_ids.filtered(
                lambda x: not rec.company_id
                or x.backend_id.company_id == rec.company_id
            ):
                raise ValidationError(
                    _(
                        "You can't modify the reference "
                        "because the lot is connected to SAP B1"
                    )
                )
