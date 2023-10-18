# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingProductSpecialSpectrum(models.Model):
    _inherit = 'lighting.product.special.spectrum'

    use_as_cct = fields.Boolean(
        string='Use as CCT',
        help='If checked, this special spectrum will be used as CCT'
             ' (Correlated Color Temperature) value in json search.'
    )
