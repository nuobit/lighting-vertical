# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LightingProductSpecialSpectrum(models.Model):
    _name = "lighting.product.special.spectrum"
    _description = "Special Spectrum"

    name = fields.Char(
        required=True,
        translate=True,
    )

    @api.constrains("name")
    def _check_name(self):
        for rec in self:
            if self.env[self._name].search_count(
                [("id", "!=", rec.id), ("name", "=ilike", rec.name)]
            ):
                raise ValidationError(
                    _("The name must be unique!"),
                )
