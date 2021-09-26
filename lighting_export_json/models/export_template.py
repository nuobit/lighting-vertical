# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import ast
import datetime
import json
import logging
import os

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

MRK_STATE_ORD = {
    x: i for i, x in enumerate(['C', 'N', 'O', 'ES', 'ESH'])
}


class LightingExportTemplate(models.Model):
    _inherit = 'lighting.export.template'

    _VALID_OBJECTS = ['labels', 'products', 'families', 'categories',
                      'groups', 'bundles', 'templates',
                      ]

    lang_field_format = fields.Selection(
        selection_add=[('json', 'Json')])

    export_labels = fields.Boolean(string="Labels")
    export_products = fields.Boolean(string="Products")
    export_categories = fields.Boolean(string="Categories")
    export_families = fields.Boolean(string="Families")
    export_templates = fields.Boolean(string="Templates")
    export_groups = fields.Boolean(string="Groups")
    export_bundles = fields.Boolean(string="Bundles")

    output_type = fields.Selection(selection_add=[('export_product_json', _('Json file (.json)'))])

    pretty_print = fields.Boolean(string="Pretty print", default=True)
    sort_keys = fields.Boolean(string="Sort keys",
                               help='If sort_keys is true (default: False), then the '
                                    'output of dictionaries will be sorted by key.', default=True)

    output_base_directory = fields.Char(string="Base directory")
    db_filestore = fields.Boolean(string="Database filestore")
    output_directory = fields.Char(string="Directory")
    output_filename_prefix = fields.Char(string="Filename prefix")

    auto_execute = fields.Boolean("Auto execute")

    link_enabled = fields.Boolean(string="Enabled")
    link_username = fields.Char(string="Username")
    link_password = fields.Char(string="Password")

    @api.onchange('db_filestore')
    def onchange_db_filestore(self):
        if self.db_filestore:
            self.output_base_directory = tools.config.filestore(self._cr.dbname)
        else:
            self.output_base_directory = False

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {},
                       name='%s (copy)' % self.name,
                       )

        return super().copy(default)

    @api.model
    def autoexecute(self):
        for t in self.env[self._name].search([('auto_execute', '=', True)]):
            t.action_json_export()

    def get_full_filepath(self, object, lang=None):
        today_str = fields.Date.from_string(fields.Date.context_today(self)).strftime('%Y%m%d')
        d = dict(object=object, date=today_str)
        if lang:
            d['lang'] = lang
        base_filename = self.output_filename_prefix % d
        filename = '%s.json' % base_filename
        parts = [self.output_base_directory]
        if self.output_directory:
            parts.append(self.output_directory)
            os.makedirs(os.path.join(*parts), mode=0o774, exist_ok=True)
        parts.append(filename)
        path = os.path.join(*parts)
        return path

    @api.multi
    def action_json_export(self):
        def default(o):
            if isinstance(o, datetime.date):
                return fields.Date.to_string(o)
            if isinstance(o, datetime.datetime):
                return fields.Datetime.to_string(o)
            if isinstance(o, set):
                return sorted(list(o))

        if not self.field_ids:
            raise UserError("You need to define at least one field")

        kwargs = {}
        if self.pretty_print:
            kwargs.update(dict(indent=4))
        if self.sort_keys:
            kwargs.update(dict(sort_keys=True))

        domain = []
        if self.domain:
            domain = ast.literal_eval(self.domain)

        objects_rs = self.env['lighting.product'].search(domain)
        object_ids = objects_rs.sorted(lambda x: x.reference).mapped('id')

        langs = self.lang_multiple_files and self.lang_ids or self.default_lang_id
        for lang in langs:
            res = self.with_context(lang=lang.code).generate_data(
                object_ids, hide_empty_fields=self.hide_empty_fields)
            for object, data in res.items():
                path = self.get_full_filepath(object, lang=lang.code)
                with open(path, 'w') as f:
                    json.dump(data, f, ensure_ascii=False, default=default, **kwargs)

    def get_efective_field_name(self, field_name):
        field = self.field_ids.filtered(lambda x: x.field_name == field_name)
        if not field:
            raise UserError("Unexpected, the field %s is not defined on template" % field_name)
        if field.effective_field_name:
            return field.effective_field_name

        return field_name

    def generate_dict(self, obj, header, hide_empty_fields=True):
        obj_d = {}
        for field, meta in header.items():
            field_d = {}
            has_value = False
            meta_langs = sorted(meta['string'].keys(),
                                key=lambda x: (0, x.code)
                                if x.code == self.env.context.get('lang', self.default_lang_id.code)
                                else (1, x.code))
            for lang in meta_langs:
                datum = getattr(obj.with_context(lang=lang.code, template_id=self), field)
                subfield = meta['subfield'] or 'display_name'
                order_field = 'sequence'
                if meta['type'] == 'selection':
                    datum = dict(meta['selection'][lang]).get(datum)
                elif meta['type'] == 'boolean':
                    if meta['translate']:
                        datum = _('Yes') if datum else _('No')
                elif meta['type'] == 'many2one':
                    value_l = datum.mapped(subfield)
                    if value_l:
                        if len(value_l) > 1:
                            raise Exception("The subfield %s value must return a singleton" % subfield)
                        datum = value_l[0]
                elif meta['type'] in ('one2many', 'many2many'):
                    datum1 = []
                    for x in datum.sorted(lambda x: order_field not in x or x[order_field]):
                        value_l = x.mapped(subfield)
                        if value_l:
                            if len(value_l) > 1:
                                raise Exception("The subfield %s value must return a singleton" % subfield)
                            datum1.append(value_l[0])
                    if datum1:
                        datum = datum1

                if meta['type'] != 'boolean' and not datum:
                    datum = None

                if datum is not None:
                    has_value = True

                ## acumulem els valors
                if not meta['translate']:
                    field_d = datum
                    break
                else:
                    if self.lang_field_format == 'json':
                        field_d[lang.code] = datum
                    elif self.lang_field_format == 'postfix':
                        field_d[lang.iso_code] = datum
                    else:
                        raise UserError("Language field format %s not supported on json templates" % (
                            self.lang_field_format))

            if has_value or not hide_empty_fields:
                if meta['effective_field_name']:
                    field = meta['effective_field_name']

                separator = meta['multivalue_separator']
                if separator:
                    if separator == 'by_field':
                        if not meta['translate']:
                            if not isinstance(field_d, list):
                                raise Exception(
                                    "Type %s no supported on Serialized fields with multivalue separator" % (
                                        type(field_d),))
                            for i, elem in enumerate(field_d, 1):
                                obj_d['%s_%02d' % (field, i)] = elem
                        else:
                            field1_d = {}
                            for lang, datum in field_d.items():
                                if not isinstance(datum, list):
                                    raise Exception(
                                        "Type %s no supported on Serialized fields with multivalue separator" % (
                                            type(field_d),))
                                for i, elem in enumerate(datum, 1):
                                    field1_d.setdefault(i, []).append((lang, elem))
                            if self.lang_field_format == 'postfix':
                                for i, langelem in field1_d.items():
                                    for lang, elem in langelem:
                                        obj_d['%s_%02d_%s' % (field, i, lang)] = elem
                            elif self.lang_field_format == 'json':
                                for i, langelem in field1_d.items():
                                    obj_d['%s_%02d' % (field, i)] = dict(langelem)
                            else:
                                raise Exception("Language field format %s not supported" % self.lang_field_format)
                    else:
                        if not meta['translate']:
                            obj_d[field] = separator.join(map(str, field_d))
                        else:
                            if self.lang_field_format == 'postfix':
                                for lang, datum in field_d.items():
                                    obj_d['%s_%s' % (field, lang)] = separator.join(map(str, datum))
                            elif self.lang_field_format == 'json':
                                obj_d[field] = field_d
                            else:
                                raise Exception("Language field format %s not supported" % self.lang_field_format)
                else:
                    if meta['translate']:
                        if self.lang_field_format == 'postfix':
                            for lang, datum in field_d.items():
                                obj_d['%s_%s' % (field, lang)] = datum
                        elif self.lang_field_format == 'json':
                            obj_d[field] = field_d
                        else:
                            raise Exception("Language field format %s not supported" % self.lang_field_format)
                    else:
                        obj_d[field] = field_d
        return obj_d

    def _generate_labels(self, header):
        _logger.info("Generating product labels...")
        label_d = {}
        for field, meta in header.items():
            if meta['effective_field_name']:
                field = meta['effective_field_name']
            if self.lang_field_format == 'json':
                label_d[field] = {k.code: v for k, v in meta['string'].items()}
            elif self.lang_field_format == 'postfix':
                for lang, label in meta['string'].items():
                    label_d['%s_%s' % (field, lang.iso_code)] = label
            else:
                raise UserError("Language field format %s not supported on json templates" % (
                    self.lang_field_format))
        _logger.info("Product labels successfully generated.")
        return label_d

    def _generate_products(self, header, object_ids, hide_empty_fields):
        n = len(object_ids)
        _logger.info("Generating %i products..." % n)
        th = int(n / 100) or 1
        objects_ld = []
        for i, object_id in enumerate(object_ids, 1):
            obj = self.env['lighting.product'].browse(object_id)
            obj_d = self.generate_dict(obj, header, hide_empty_fields)
            if obj_d:
                objects_ld.append(obj_d)

            if (i % th) == 0:
                _logger.info(" - Progress products generation %i%%" % (int(i / n * 100)))
        _logger.info("Products successfully generated...")
        return objects_ld

    def _generate_bundles(self, template_d):
        _logger.info("Generating bundle products...")
        # generem els bundles agrupant cada bundle i posant dins tots els tempaltes
        # dels requireds associats
        bundle_d = {}
        for template_name, objects_l in template_d.items():
            products = self.env['lighting.product'].browse([x.id for x in objects_l])
            is_bundle_template = any(products.mapped('is_composite'))
            if is_bundle_template:
                # state
                bundle_d[template_name] = {
                    'enabled': any(products.mapped('website_published')),
                }

                # bundle name
                bundle_name_d = {}
                for lang in self.lang_ids:
                    lang_group_description = products[0].with_context(lang=lang.code).group_description
                    if lang_group_description:
                        bundle_name_d[lang.code] = lang_group_description

                if bundle_name_d:
                    # temporary solution to not break integration
                    if 'es_ES' in bundle_name_d:
                        bundle_d[template_name].update({
                            'name': bundle_name_d['es_ES'],
                        })

                # required products
                domain = [('id', 'in', products.mapped('required_ids.id'))]
                if self.domain:
                    domain += ast.literal_eval(self.domain)
                products_required = self.env['lighting.product'].search(domain)
                if products_required:
                    ## components
                    bundle_d[template_name].update({
                        'templates': sorted(list(set(products_required.mapped('finish_group_name'))))
                    })

                    ## default attach
                    attachment_order_d = {x.type_id: x.sequence for x in self.attachment_ids}
                    # first own attachments
                    attachment_ids = products.mapped('attachment_ids') \
                        .filtered(lambda x: x.type_id.is_image and
                                            x.type_id in attachment_order_d.keys()) \
                        .sorted(lambda x: (attachment_order_d[x.type_id], x.sequence, x.id))

                    # after required attachments
                    if not attachment_ids:
                        attachment_ids = products_required.mapped('attachment_ids') \
                            .filtered(lambda x: x.type_id.is_image and
                                                x.type_id in attachment_order_d.keys()) \
                            .sorted(lambda x: (attachment_order_d[x.type_id], x.sequence, x.id))
                    if attachment_ids:
                        bundle_d[template_name].update({
                            'attachment': {
                                'datas_fname': attachment_ids[0].datas_fname,
                                'store_fname': attachment_ids[0].attachment_id.store_fname,
                            }
                        })
        _logger.info("Bundle products successfully generated...")
        return bundle_d

    def _generate_templates(self, template_d, objects_d):
        _logger.info("Generating configurable products (grouped by finish)...")
        # comprovem que les templates rene  mes dun element, sino, l'eliminem
        # escollim un objecte qualsevol o generalm al descricio sense el finish
        template_clean_d = {}
        for k, v in template_d.items():
            if len(v) > 1:
                products = self.env['lighting.product'].browse([p.id for p in v])

                ## state
                template_clean_d[k] = {
                    'enabled': any(products.mapped('website_published')),
                }

                ## description
                template_desc_d = {}
                for lang in self.lang_ids:
                    lang_description = v[0].with_context(lang=lang.code)._generate_description(
                        show_variant_data=False)
                    if lang_description:
                        template_desc_d[lang.code] = lang_description
                if template_desc_d:
                    if k not in template_clean_d:
                        template_clean_d[k] = {}
                    template_clean_d[k].update({
                        'description': template_desc_d
                    })

                ## default attach
                attachment_order_d = {x.type_id: x.sequence for x in self.attachment_ids}
                attachment_ids = products.mapped('attachment_ids') \
                    .filtered(lambda x: x.type_id.is_image and
                                        x.type_id in attachment_order_d.keys()) \
                    .sorted(lambda x: (attachment_order_d[x.type_id], x.sequence, x.id))
                if attachment_ids:
                    if k not in template_clean_d:
                        template_clean_d[k] = {}
                    template_clean_d[k].update({
                        'attachment': {
                            'datas_fname': attachment_ids[0].datas_fname,
                            'store_fname': attachment_ids[0].attachment_id.store_fname,
                        }
                    })

                ### common attributes
                field_ids = products.mapped('product_group_id.field_ids')

                ## merge common fields with attributes from the category
                field_ids |= products.mapped('category_id.effective_attribute_ids')

                product_data = {}
                fields = [self.get_efective_field_name(x.name) for x in field_ids]
                for f in fields:
                    for product in products.sorted(
                            lambda x: (MRK_STATE_ORD.get(x.state_marketing, len(MRK_STATE_ORD)), x.sequence)):
                        if f in product_data:
                            break
                        if f in objects_d[product.reference]:
                            product_data[f] = objects_d[product.reference][f]
                            break

                if product_data:
                    template_clean_d[k].update(product_data)
        _logger.info("Configurable products successfully generated...")
        return template_clean_d

    def _generate_groups(self, photo_group_d, objects_d):
        _logger.info("Generating product groups...")
        groups_d = {}
        for group, products in photo_group_d.items():
            # if the group does not contain any bundle
            if not any(products.mapped('is_composite')) and not any(products.mapped('is_required_accessory')):
                group_d = {}

                ## products
                group_d.update({
                    'product': sorted(list(set(products.mapped('finish_group_name')))),
                })

                ## catalog
                catalog_ids = products.mapped('catalog_ids')
                if catalog_ids:
                    group_d.update({
                        'catalog': sorted(list(set(catalog_ids.mapped('name')))),
                    })

                ## attributes
                if group.attribute_ids:
                    attributes = [self.get_efective_field_name(x.name) for x in group.attribute_ids]
                    group_d.update({
                        'product_attribute': sorted(attributes),
                    })

                ## common fields
                product_data = {}
                fields = [self.get_efective_field_name(x.name) for x in group.field_ids]
                for f in fields:
                    for product in products.sorted(
                            lambda x: (MRK_STATE_ORD.get(x.state_marketing, len(MRK_STATE_ORD)), x.sequence)):
                        if f in product_data:
                            break
                        if f in objects_d[product.reference]:
                            product_data[f] = objects_d[product.reference][f]
                            break

                # description (is a common field too)
                product = products[0].with_context(template_id=self)
                group_desc_d = {}
                for lang in self.lang_ids:
                    lang_group_description = product.with_context(lang=lang.code).group_description
                    if lang_group_description:
                        group_desc_d[lang.code] = lang_group_description

                if group_desc_d:
                    product_data.update({
                        'description': group_desc_d,
                    })

                if product_data:
                    group_d.update({
                        'common_attribute': product_data,
                    })

                if group_d:
                    groups_d[group.name] = group_d
        _logger.info("Product groups successfully generated...")
        return groups_d

    def _generate_families(self, object_ids):
        ## generm la informacio de les families
        _logger.info("Generating family data...")
        # obtenim els ids de es fmailie sel sobjectes seleccionats
        objects = self.env['lighting.product'].browse(object_ids)
        families = objects.mapped('family_ids')
        if families:
            family_ld = []
            for family in families.sorted(lambda x: x.sequence):
                family_d = {}
                # descricpio llarga
                family_descr_lang = {}
                for lang in self.lang_ids:
                    descr = family.with_context(lang=lang.code).description
                    if descr:
                        family_descr_lang[lang.code] = descr
                if family_descr_lang:
                    family_d.update({
                        'description': family_descr_lang,
                    })
                # adjunts ordenats
                if family.attachment_ids:
                    attachments = family.attachment_ids \
                        .filtered(lambda x: x.is_default) \
                        .sorted(lambda x: (x.sequence, x.id))
                    if attachments:
                        family_d.update({
                            'attachment': {
                                'datas_fname': attachments[0].datas_fname,
                                'store_fname': attachments[0].attachment_id.store_fname,
                            },
                        })

                # nom: si la familia te dades, afegim el nom i lafegim, sino no
                if family_d:
                    family_d.update({
                        'name': family.name,
                    })
                    family_ld.append(family_d)
            _logger.info("Family data successfully generated...")
            return family_ld

    def _generate_categories(self, categories):
        ## generem la informacio de les categories
        _logger.info("Generating category data...")
        category_ld = []
        for category in categories.sorted(lambda x: x.sequence):
            category_d = {
                'id': category.id,
            }
            if category.attachment_ids:
                category_attach_d = {}

                # brands OLD
                brand_attach_d = {}
                brand_attachments = category.attachment_ids \
                    .filtered(lambda x: x.brand_id) \
                    .sorted(lambda x: (x.sequence, x.id))
                for a in brand_attachments:
                    brand = a.brand_id.name
                    if brand not in brand_attach_d:
                        brand_attach_d[brand] = {
                            'datas_fname': a.datas_fname,
                            'store_fname': a.attachment_id.store_fname,
                        }
                if brand_attach_d:
                    category_attach_d.update({
                        'catalog': brand_attach_d,
                    })

                # location OLD
                location_attach_d = {}
                location_attachments = category.attachment_ids \
                    .filtered(lambda x: x.location_id) \
                    .sorted(lambda x: (x.sequence, x.id))
                if location_attachments:
                    a = location_attachments[0]
                    location_attach_d = {
                        'datas_fname': a.datas_fname,
                        'store_fname': a.attachment_id.store_fname,
                    }
                if location_attach_d:
                    category_attach_d.update({
                        'location': location_attach_d,
                    })

                # global
                if not category_attach_d:
                    global_attach_d = {}
                    global_attachments = category.attachment_ids \
                        .sorted(lambda x: (x.sequence, x.id))
                    if global_attachments:
                        a = global_attachments[0]
                        global_attach_d = {
                            'datas_fname': a.datas_fname,
                            'store_fname': a.attachment_id.store_fname,
                        }
                    if global_attach_d:
                        category_attach_d.update({
                            None: global_attach_d,
                        })

                # category attach OLD
                if category_attach_d:
                    category_d.update({
                        'attachment': category_attach_d,
                    })

                category_attach_d = {}

                # brands NEW
                brand_attach_d = {}
                brand_attachments = category.attachment_ids \
                    .sorted(lambda x: (x.sequence, x.id))
                for a in brand_attachments:
                    brand = not a.brand_default and a.brand_id.name or None
                    if brand not in brand_attach_d:
                        brand_attach_d[brand] = {
                            'datas_fname': a.datas_fname,
                            'store_fname': a.attachment_id.store_fname,
                        }
                if brand_attach_d:
                    category_attach_d.update({
                        'catalog': brand_attach_d,
                    })

                # location NEW
                location_attachments = category.attachment_ids \
                    .sorted(lambda x: (x.sequence, x.id))
                location_attach_d = {}
                for la in location_attachments:
                    location_code = not la.location_default and la.location_id.code or None
                    if location_code not in location_attach_d:
                        location_attach_d[location_code] = {
                            'datas_fname': a.datas_fname,
                            'store_fname': a.attachment_id.store_fname,
                        }
                if location_attach_d:
                    category_attach_d.update({
                        'location': location_attach_d,
                    })

                # category attach NEW
                if category_attach_d:
                    category_d.update({
                        'attachmentNEW': category_attach_d,
                    })

            # nom de la categoria
            name_lang_d = {}
            for lang in self.lang_ids:
                lang_name = category.with_context(lang=lang.code).name
                if lang_name:
                    name_lang_d[lang.code] = lang_name
            if name_lang_d:
                category_d.update({
                    'name': name_lang_d,
                })

            if category_d:
                category_ld.append(category_d)
        _logger.info("Category data successfully generated...")
        return category_ld

    def _generate_product_header(self):
        ## base headers with labels replaced and subset acoridng to template
        _logger.info("Generating product headers...")
        header = {}
        for line in self.field_ids.sorted(lambda x: x.sequence):
            field_name = line.field_id.name
            item = {}
            for lang in self.lang_ids:
                item_lang = self.env['lighting.product']. \
                    with_context(lang=lang.code).fields_get([field_name], ['type', 'string', 'selection'])
                if item_lang:
                    meta = item_lang[field_name]
                    for k, v in meta.items():
                        if k in ('type',):
                            if k not in item:
                                item[k] = v
                        else:
                            if k == 'string':
                                line_lang = line.with_context(lang=lang.code)
                                if line_lang.label and line_lang.label.strip():
                                    v = line_lang.label

                            if k not in item:
                                item[k] = {}

                            item[k][lang] = v
            if item:
                item['effective_field_name'] = line.effective_field_name
                item['subfield'] = line.subfield_name
                item['multivalue_separator'] = line.multivalue_separator
                item['translate'] = line.translate
                header[field_name] = item
        _logger.info("Product headers successfully generated.")
        return header

    ############ AUXILIARS  #####
    def _groups_by_finish(self, object_ids):
        ## auxiliar per agrupar referneeicas amb el mateix finish
        _logger.info("Generating dictionary of groups by finish...")
        template_d = {}
        for obj_id in object_ids:
            obj = self.env['lighting.product'].browse(obj_id)
            template_name = getattr(obj, 'finish_group_name', None)
            if template_name:
                if template_name not in template_d:
                    template_d[template_name] = []
                template_d[template_name].append(obj)
        _logger.info("Dictionary of groups by finish successfully generated.")
        return template_d

    def _groups_by_photo(self, object_ids):
        ## auxiliar per agrupar referneeicas amb el mateixa photo
        _logger.info("Generating dictionary of groups by photo...")
        photo_group_d = {}
        for obj_id in object_ids:
            obj = self.env['lighting.product'].browse(obj_id)
            group_id = getattr(obj, 'photo_group_id', None)
            if group_id:
                if group_id not in photo_group_d:
                    photo_group_d[group_id] = self.env['lighting.product']
                photo_group_d[group_id] += obj
        _logger.info("Dictionary of groups by photo successfully generated.")
        return photo_group_d

    def _products_by_reference(self, objects_ld):
        ### per poder indexat els prodductes i brenir les dades directament
        _logger.info("Generating dictionary of products...")
        objects_d = {}
        for obj in objects_ld:
            key = obj['reference']
            if key in objects_d:
                raise Exception("Unexpected!! The key %s is duplicated!" % key)
            objects_d[key] = obj
        _logger.info("Dictionary of products successfully generated.")
        return objects_d

    ###### MAIN method
    def generate_data(self, object_ids, hide_empty_fields=True):
        _logger.info("Export data started...")

        ####### HEADER ########
        header = self._generate_product_header()

        res = {}
        ############## LABELS ################
        if self.export_labels:
            res.update({'labels': self._generate_labels(header)})

        ############## PRODUCTS ################
        objects_ld = self._generate_products(header, object_ids, hide_empty_fields)
        if self.export_products:
            res.update({'products': objects_ld})

        ############## FAMILIES ###############
        if self.export_families:
            if objects_ld:
                res.update({'families': self._generate_families(object_ids)})

        ############## CATEGORIES ################
        if self.export_categories:
            if objects_ld:
                objects = self.env['lighting.product'].browse(object_ids)
                categories = objects.mapped('category_id.root_id')
                if categories:
                    res.update({'categories': self._generate_categories(categories)})

        objects_d = None
        ############## GROUPS ################
        if self.export_groups:
            photo_group_d = self._groups_by_photo(object_ids)
            objects_d = self._products_by_reference(objects_ld)
            res.update({'groups': self._generate_groups(photo_group_d, objects_d)})

        template_d = None
        ############## BUNDLES (by finish) ################
        if self.export_bundles:
            template_d = self._groups_by_finish(object_ids)
            res.update({'bundles': self._generate_bundles(template_d)})

        ############## CONFIGURABLES (by finish) ################
        if self.export_templates:
            if template_d is None:
                template_d = self._groups_by_finish(object_ids)
            if objects_d is None:
                objects_d = self._products_by_reference(objects_ld)
            res.update({'templates': self._generate_templates(template_d, objects_d)})

        _logger.info("Export data successfully done")

        return res
