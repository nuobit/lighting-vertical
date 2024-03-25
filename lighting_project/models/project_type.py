# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LightingProjectType(models.Model):
    _name = 'lighting.project.type'
    _order = 'name'

    name = fields.Char(string='Name', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', 'The keyword must be unique!'),
                        ]
