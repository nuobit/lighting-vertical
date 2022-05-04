# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping)

from odoo.exceptions import ValidationError


class LigthingProductExportMapper(Component):
    _name = 'sapb1.lighting.product.export.mapper'
    _inherit = 'sapb1.lighting.export.mapper'

    _apply_on = 'sapb1.lighting.product'

    @mapping
    def catalog(self, record):
        if len(record.catalog_ids) != 1:
            raise ValidationError("Reference must belong to only 1 catalog")
        sap_item_group_id = self.backend_record.catalog_map \
            .filtered(lambda x: x.catalog_id == record.catalog_ids) \
            .sap_item_group_id
        if not sap_item_group_id:
            raise ValidationError(
                "There's no mapping of %s on Backend configuration" % (record.catalog_ids.name,))

        return {'ItemsGroupCode': sap_item_group_id}

    @mapping
    def state_marketing(self, record):
        sap_state_reference = None
        if record.state_marketing:
            sap_state_reference = self.backend_record.state_marketing_map \
                .filtered(lambda x: x.state_marketing == record.state_marketing) \
                .sap_state_reference
            if not sap_state_reference:
                raise ValidationError(f"The Marketing State %s has no mapping"
                                      f" to SAP ID in the Backend configuration")
        return {'U_ACC_Obsmark': sap_state_reference}

    @mapping
    def family(self, record):
        return {'U_U_familia': ', '.join(
            sorted(record.family_ids.mapped("name")))
        }

    @mapping
    def category(self, record):
        if not self.backend_record.language_map:
            raise ValidationError("There's no language mapping "
                                  "in the Backend configuration")
        values = {}
        for lmap in self.backend_record.language_map:
            values[lmap.sap_lang_id] = record.with_context(lang=lmap.lang_id.code).category_id._get_root().name
        return {'U_U_aplicacion': values}

    @mapping
    def configurator(self, record):
        return {'U_U_Configurador': record.configurator or None}
