# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import re
import decimal

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (
    mapping, external_to_m2o, only_create)
from odoo.exceptions import ValidationError

ACCESSORY_CATALOG = 'NX Lighting'


class LigthingProductImportMapper(Component):
    _name = 'sapb1.lighting.product.import.mapper'
    _inherit = 'sapb1.import.mapper'

    _apply_on = 'sapb1.lighting.product'

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def content_hash(self, record):
        return {'external_content_hash': record['Hash']}

    @mapping
    def ean_codebar(self, record):
        return {'ean': record['CodeBars'] and
                       record['CodeBars'].strip() or None}

    @mapping
    def stock(self, record):
        values = {}

        values['onhand_qty'] = record['OnHand']
        values['commited_qty'] = record['IsCommited']

        capacity_qty = record['Capacity'] > 0 and record['Capacity'] or 0
        values['capacity_qty'] = capacity_qty

        available_qty = (record['OnHand'] or 0) - (record['IsCommited'] or 0)
        values['available_qty'] = (available_qty > 0 and available_qty or 0) + capacity_qty

        values['onorder_qty'] = record['OnOrder']

        values['stock_future_date'] = record['ShipDate']
        values['stock_future_qty'] = record['ShipDate'] and (available_qty + (record['OnOrder'] or 0)) or 0

        return values

    @mapping
    def last_purchase_date(self, record):
        return {'last_purchase_date': record['LastPurDat']}

    def _get_currency_id_by_name(self, name):
        price_currency_id = None
        if name:
            price_currency = self.env['res.currency'].search([
                ('name', '=', name),
            ])
            if price_currency:
                price_currency_id = price_currency.id

        return price_currency_id

    @mapping
    def price(self, record):
        return {'price': record['Price'],
                'price_currency_id': self._get_currency_id_by_name(record['Currency'])}

    @mapping
    def cost(self, record):
        return {'cost': record['PurchasePrice'],
                'cost_currency_id': self._get_currency_id_by_name(record['PurchasePriceCurrency'])}

    @mapping
    def dimensions(self, record):
        binding = self.options.get('binding')
        values = {}
        if not binding or not binding.ibox_weight:
            values['ibox_weight'] = record['SWeight1']
        if not binding or not binding.ibox_volume:
            values['ibox_volume'] = record['SVolume'] * 1000
        if not binding or not binding.ibox_length:
            values['ibox_length'] = record['SLength1']
        if not binding or not binding.ibox_width:
            values['ibox_width'] = record['SWidth1']
        if not binding or not binding.ibox_height:
            values['ibox_height'] = record['SHeight1']
        return values

    @only_create
    @mapping
    def description_manual(self, record):
        return {'description_manual': record['ItemName'] and
                                      record['ItemName'].strip() or None}

    @only_create
    @mapping
    def state_marketing(self, record):
        u_acc_obsmark = record['U_ACC_Obsmark'] and record['U_ACC_Obsmark'].strip() or None
        if u_acc_obsmark:
            state_marketing = self.backend_record.state_marketing_map \
                .filtered(lambda x: x.sap_state_reference == u_acc_obsmark) \
                .state_marketing
            if not state_marketing:
                raise ValidationError("There's no mapping to %s in the Backend configuration" % (u_acc_obsmark,))
            return {
                'state_marketing': state_marketing,
            }

    @only_create
    @mapping
    def catalog(self, record):
        catalog = self.backend_record.catalog_map.filtered(
            lambda x: x.sap_item_group_id == record['ItmsGrpCod']
        ).catalog_id
        if not catalog:
            raise ValidationError("There's no mapping for %s configured in Backend" % record['ItmsGrpCod'])

        return {
            'catalog_ids': [(6, False, catalog.ids)],
        }

    @only_create
    @mapping
    def family_ids(self, record):
        families = None
        familia = record['U_U_familia'] and record['U_U_familia'].strip() or None
        familia = familia != '-' and familia or None
        if not familia:
            item_code = record['ItemCode'].strip()
            references = self._get_sibling_reference(item_code, "^(.+)-[^-]{2}")
            if references:
                families = references.mapped('family_ids')

            if not families:
                references = self._get_sibling_reference(item_code, "^([^-]+)-.+$")
                if not references:
                    references = self._get_sibling_reference(item_code, "^([A-Z0-9][0-9]{2})[A-Z]-.+$")
                if references:
                    reference_groups = {}
                    for r in references:
                        for f in r.family_ids:
                            reference_groups.setdefault(f, 0)
                            reference_groups[f] += 1
                    if reference_groups:
                        families = sorted(reference_groups.items(),
                                          key=lambda x: x[1], reverse=True)[0][0]
        else:
            families = self.env['lighting.product.family'].search([
                ('name', '=ilike', familia),
            ])

        if families:
            return {'family_ids': [(6, False, families.ids)]}

    @only_create
    @mapping
    def category_id(self, record):
        category = None
        aplicacion = record['U_U_aplicacion'] and record['U_U_aplicacion'].strip() or None
        if not aplicacion:
            references = self._get_sibling_reference(record['ItemCode'].strip(), "^(.+)-[^-]{2}")
            if references:
                category = references.mapped('category_id')
                if len(category) > 1:
                    raise Exception(_("The other variants have more than one category '%s', "
                                      "it's not possible to infer the category.") % (category,))
        else:
            complete_name = aplicacion
            m = re.match(r'^([^/]+) *\/ *(.+)$', aplicacion)
            if m:
                complete_name = ' / '.join(m.groups())

            category = self.env['lighting.product.category'] \
                .with_context(lang='es_ES') \
                .search([('complete_name', '=ilike', complete_name)])
            if len(category) > 1:
                raise Exception(_("Multiple Category %s found") % (', '.join(category.mapped('name')),))

        if not category:
            catalog_name = record['ItmsGrpNam'] and record['ItmsGrpNam'].strip() or None
            if catalog_name == ACCESSORY_CATALOG:
                category = self.env['lighting.product.category'] \
                    .with_context(lang='es_ES') \
                    .search([
                    ('parent_id', '=', False),
                    ('name', '=', 'Accesorios'),
                ])
                if len(category) > 1:
                    raise Exception(_("Multiple Accessory category %s found") % (', '.join(category.mapped('name')),))

        if category:
            return {'category_id': category.id}

    @only_create
    @mapping
    def reference(self, record):
        return {'reference': record['ItemCode'] and record['ItemCode'].strip() or None}

    # aux
    def _get_sibling_reference(self, reference, pattern):
        m = re.match(pattern, reference)
        if not m:
            return None

        reference_prefix = m.group(1)
        references = self.env['lighting.product'].search([
            ('reference', '=like', '%s%%' % reference_prefix),
        ])

        return references

    def finalize(self, map_record, values):
        if values.get('family_ids') and values.get('category_id') \
                and values.get('location_ids'):
            values['state'] = 'published'

        return values
