# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api

from odoo.addons.queue_job.job import job


class LightingProduct(models.Model):
    _inherit = 'lighting.product'

    sapb1_bind_ids = fields.One2many(
        comodel_name='sapb1.lighting.product',
        inverse_name='odoo_id',
        string='SAP B1 Bindings',
    )


class LightingProductBinding(models.Model):
    _name = 'sapb1.lighting.product'
    _inherit = 'sapb1.binding'
    _inherits = {'lighting.product': 'odoo_id'}

    odoo_id = fields.Many2one(comodel_name='lighting.product',
                              string='Product',
                              required=True,
                              ondelete='cascade')

    @job(default_channel='root.sapb1')
    def import_products_since(self, backend_record=None):
        """ Prepare the batch import of products modified on SAP B1 """
        filters = []
        existing_hashes = self.env['sapb1.lighting.product'].search([
            ('external_content_hash', '!=', False),
        ]).mapped('external_content_hash')
        if existing_hashes:
            filters = [('Hash', 'not in', existing_hashes)]
        now_fmt = fields.Datetime.now()
        self.env['sapb1.lighting.product'].import_batch(
            backend=backend_record, filters=filters)
        backend_record.import_products_since_date = now_fmt

        return True

    @job(default_channel='root.sapb1')
    def export_products_since(self, backend_record=None):
        """ Prepare the batch export of products modified on Odoo """
        domain = []  # ('reference', '=', '007A-G05X1A-01')]
        if backend_record.export_products_since_date:
            domain += [
                ('write_date', '>', backend_record.export_products_since_date),
            ]
        now_fmt = fields.Datetime.now()
        self.env['sapb1.lighting.product'].export_batch(
            backend=backend_record, domain=domain)
        backend_record.export_products_since_date = now_fmt

        return True

    @api.multi
    def resync_import(self):
        for record in self:
            with record.backend_id.work_on(record._name) as work:
                binder = work.component(usage='binder')
                external_id = binder.to_external(self)

            func = record.import_record
            if record.env.context.get('connector_delay'):
                func = record.import_record.delay

            func(record.backend_id, external_id)

        return True

    def resync_export(self):
        for record in self:
            with record.backend_id.work_on(record._name) as work:
                binder = work.component(usage="binder")
                relation = binder.unwrap_binding(record)

            func = record.export_record
            if record.env.context.get("connector_delay"):
                func = func.with_delay

            func(record.backend_id, relation)

        return True
