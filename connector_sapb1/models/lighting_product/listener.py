# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class SAPB1LightingProductImporter(Component):
    _name = "sapb1.lighting.product.listener"
    _inherit = "sapb1.listener"

    _apply_on = "lighting.product"

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        relevant_fields = {
            'description', 'category_id',
            'family_ids', 'state_marketing', 'catalog_ids', 'configurator'
        }
        if 'state' in fields:
            if record.state == 'published':
                relevant_fields.add('state')
        if fields is None or relevant_fields & set(fields):
            for backend in record.sudo().sapb1_bind_ids.mapped('backend_id'):
                self.env["sapb1.lighting.product"].sudo(backend.user_id) \
                    .with_delay().export_record(backend.sudo(backend.user_id), record)
