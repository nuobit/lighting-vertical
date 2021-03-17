# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


def chunks(li, n):
    if not li:
        return
    yield li[:n]
    yield from chunks(li[n:], n)


class LightingReportingProductDatasheetWizard(models.TransientModel):
    _name = "lighting.reporting.product.datasheet.wizard"

    def _default_lang_id(self):
        lang = self.env.context.get('lang')
        if lang:
            return self.env['res.lang'].search([('code', '=', lang)]).id
        return False

    lang_id = fields.Many2one(string='Language', comodel_name='res.lang', default=_default_lang_id)

    only_generate_background = fields.Boolean(string="Generate only (in background)")
    force_update = fields.Boolean(string="Force update")

    @api.multi
    def print_product_datasheet(self):
        model = self.env.context.get('active_model')
        products = self.env[model].browse(self.env.context.get('active_ids'))
        if self.only_generate_background:
            ir_config = self.env['ir.config_parameter'].sudo()
            chunk_size = int(ir_config.get_param('lighting.datasheet.prepare.chunk.size', 25))
            ck_num = int(len(products) / chunk_size)
            for ck in chunks(products, ck_num):
                ck.with_delay().update_product_datasheets(
                    lang_ids=self.lang_id.id, delayed=True, force_update=self.force_update)
        else:
            lang = self.env['res.lang'].search([
                ('code', '=', self.lang_id.code)
            ])
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/datasheets/%i/%s' % (lang.id, ','.join([str(x) for x in products.ids])),
                'target': 'new',
                'context': {'pepe': 'ooo'}
            }
