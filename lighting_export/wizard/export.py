# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LightingExport(models.TransientModel):
    _name = "lighting.export"
    _description = "Export data"

    template_id = fields.Many2one(comodel_name='lighting.export.template', ondelete='set null',
                                  string='Template', required=True)

    interval = fields.Selection(selection=[('all', _('All')), ('selection', _('Selection'))], default='selection')

    @api.multi
    def export_product_xlsx(self):
        self.ensure_one()

        return {
            'name': 'Lighting product XLSX report',
            'model': 'lighting.product',
            'type': 'ir.actions.report',
            'report_name': 'lighting_export.export_product_xlsx',
            'report_type': 'xlsx',
            'report_file': 'export.product',
            'data': {'interval': self.interval,
                     'template_id': self.template_id.id,
                     },
        }
