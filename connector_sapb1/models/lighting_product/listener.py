# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class SAPB1LightingProductImporter(Component):
    _name = "sapb1.lighting.product.listener"
    _inherit = "sapb1.listener"

    _apply_on = "lighting.product"

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        for backend in record.sapb1_bind_ids.mapped('backend_id'):
            self.env["sapb1.lighting.product"].with_delay().export_record(backend, record)
