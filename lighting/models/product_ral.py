# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class LightingProductRal(models.Model):
    _name = 'lighting.product.ral'
    _order = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Description', required=True, translate=True)

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count([
                ('ral_id', '=', record.id)
            ])

    _sql_constraints = [('name_uniq', 'unique (name)', 'The ral name must be unique!'),
                        ('code_uniq', 'unique (code)', 'The ral code must be unique!'),
                        ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '[RAL %s] %s' % (record.code, record.name)
            vals.append((record.id, name))

        return vals
