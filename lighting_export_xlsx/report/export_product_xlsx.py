# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import _, models

_logger = logging.getLogger(__name__)


class ExportProductXlsx(models.AbstractModel):
    _name = 'report.lighting_export_xlsx.export_product_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_workbook_options(self):
        return {'strings_to_urls': False}

    def generate_xlsx_report(self, workbook, data, objects):
        self.with_context(lang=data['lang']).generate_xlsx_report_ctx(workbook, data, objects)

    def generate_xlsx_report_ctx(self, workbook, data, objects):
        template_id = self.env['lighting.export.template'].browse(data.get('template_id'))

        if data.get('interval') == 'all':
            active_model = self.env.context.get('active_model')
            active_domain = data.get('context').get('active_domain')
            objects = self.env[active_model].search(active_domain)
        else:
            objects = self.env['lighting.product'].browse(data.get('active_ids'))
        if data.get('exclude_configurator'):
            objects = objects.filtered(
                lambda x: not x.configurator)

        ## base headers with labels replaced and subset acoridng to template
        header = []
        for line in template_id.field_ids.sorted(lambda x: x.sequence):
            item = objects.fields_get([line.field_id.name], ['string', 'type', 'selection'])
            if item:
                field, meta = tuple(item.items())[0]
                if line.label and line.label.strip():
                    meta['string'] = line.label
                meta.update(dict(num=0, subfields=None))
                header.append((field, meta))

        ## generate data and gather header data
        objects_ld = self._generate_products(header, objects.ids, template_id)

        ## generate xlsx headers according to data
        xlsx_header = []
        for field, meta in header:
            if not meta['num'] and data.get('hide_empty_fields'):
                continue
            if not meta['subfields']:
                xlsx_header.append(meta['string'])
            else:
                for sf in meta['subfields']:
                    xlsx_header.append(sf)

        ## write to xlsx
        sheet = workbook.add_worksheet(template_id.display_name)
        row = col = 0

        # write header to xlsx
        bold = workbook.add_format({'bold': True})
        for col_header in xlsx_header:
            sheet.write(row, col, col_header, bold)
            col += 1

        # write data to xlsx according to header multiplicity
        row = 1
        for obj in objects_ld:
            col = 0
            for field, meta in header:
                if not meta['num'] and data.get('hide_empty_fields'):
                    continue

                if not meta['subfields']:
                    sheet.write(row, col, obj[meta['string']])
                    col += 1
                else:
                    for k in meta['subfields']:
                        sheet.write(row, col, obj.get(k))
                        col += 1
            row += 1

    def _generate_products(self, header, object_ids, template_id):
        n = len(object_ids)
        _logger.info("Generating %i products..." % n)
        th = int(n / 100) or 1
        objects_ld = []
        for i, obj_id in enumerate(object_ids, 1):
            obj = self.env['lighting.product'].browse(obj_id)
            obj_d = {}
            for field, meta in header:
                datum = getattr(obj, field)
                if meta['type'] == 'selection':
                    datum = dict(meta['selection']).get(datum)
                elif meta['type'] == 'many2many':
                    datum = ','.join([x.display_name for x in datum])
                elif meta['type'] == 'boolean':
                    datum = _('Yes') if datum else _('No')
                elif meta['type'] == 'many2one':
                    datum = datum.display_name
                elif meta['type'] == 'one2many':
                    if hasattr(datum, 'export_xlsx'):
                        datum = datum.export_xlsx(template_id)
                    else:
                        datum = None  # NOT SUPPORTED

                if meta['type'] != 'boolean' and not datum:
                    datum = None

                if isinstance(datum, (tuple, list)):
                    subfields = []
                    for j, sf in enumerate(datum, 1):
                        ## update x als headers
                        sf1 = list(sf.keys())
                        if subfields:
                            if set(subfields) != set(sf1):
                                raise Exception("Unexpected Error")
                        else:
                            subfields = sf1

                        ## afegim dades
                        fnam = '%s%i' % (meta['string'], j)
                        for k, v in sf.items():
                            sfkey = '%s/%s' % (fnam, k)
                            if sfkey in obj_d:
                                raise Exception("The subfield '%s' is duplicated" % sfkey)
                            obj_d[sfkey] = v

                            if not meta['subfields']:
                                meta['subfields'] = []
                            if sfkey not in meta['subfields']:
                                meta['subfields'].append(sfkey)

                    meta['num'] = max(meta['num'], len(datum))
                else:
                    fkey = meta['string']
                    if fkey in obj_d:
                        raise Exception("The field '%s' is duplicated" % fkey)
                    obj_d[fkey] = datum

                    if not meta['num'] and datum:
                        meta['num'] = 1

            objects_ld.append(obj_d)

            if (i % th) == 0:
                _logger.info(" - Progress products generation %i%%" % round(i / n * 100))

        _logger.info("Products successfully generated...")

        return objects_ld
