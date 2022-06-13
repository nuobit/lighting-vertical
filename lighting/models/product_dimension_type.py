# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _


class LightingDimensionType(models.Model):
    _name = 'lighting.dimension.type'
    _order = 'name'

    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True, help='Code used to identify the dimension type')
    uom = fields.Char(string='Uom', help='Unit of mesure')
    description = fields.Char(string='Internal description')

    _sql_constraints = [
        ('name_uniq', 'unique (name, uom)', 'The dimension name must be unique!'),
        ('code_uniq', 'unique (code)', 'The dimension code must be unique!'),
    ]

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name_l = [record.name]
            if record.uom:
                name_l.append('(%s)' % record.uom)
            vals.append((record.id, ' '.join(name_l)))

        return vals
