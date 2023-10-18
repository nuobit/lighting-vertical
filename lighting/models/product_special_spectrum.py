# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models, api
from odoo.exceptions import ValidationError


class LightingProductSpecialSpectrum(models.Model):
    _name = 'lighting.product.special.spectrum'
    _description = 'Special Spectrum'

    name = fields.Char(string='Name', required=True, translate=True)

    @api.constrains("name")
    def _check_name(self):
        for record in self:
            if self.env[self._name].search_count(
                [("id", "!=", record.id), ("name", "=ilike", record.name)]
            ):
                raise ValidationError(
                    _("The name must be unique!"),
                )
