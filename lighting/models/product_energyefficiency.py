# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree

from collections import OrderedDict


class LightingEnergyEfficiency(models.Model):
    _name = 'lighting.energyefficiency'
    _order = 'sequence'

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")
    name = fields.Char(string='Description', required=True)

    color = fields.Integer(string='Color Index')

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count([
                ('source_ids.line_ids.efficiency_ids', 'in', record.ids),
            ])

    _sql_constraints = [('name_uniq', 'unique (name)', 'The energy efficiency must be unique!'),
                        ]

    @api.multi
    def unlink(self):
        records = self.env['lighting.product.source.line'].search([
            ('efficiency_ids', 'in', self.ids),
        ])
        if records:
            raise UserError(_("You are trying to delete a record that is still referenced by products %s") %
                            records.mapped('source_id.product_id.reference'))
        return super(LightingEnergyEfficiency, self).unlink()
