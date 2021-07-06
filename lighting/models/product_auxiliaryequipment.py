# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree

from collections import OrderedDict


class LightingProductAuxiliaryEquipment(models.Model):
    _name = 'lighting.product.auxiliaryequipment'
    _order = 'name'

    name = fields.Char(string='Auxiliary equipment', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The auxiliary equipment must be unique!'),
                        ]

    @api.multi
    def unlink(self):
        records = self.env['lighting.product'].search([('auxiliary_equipment_ids', 'in', self.ids)])
        if records:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(LightingProductAuxiliaryEquipment, self).unlink()
