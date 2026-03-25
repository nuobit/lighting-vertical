# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import json
import logging

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import human_size

_logger = logging.getLogger(__name__)


class ExportProductXlsx(models.AbstractModel):
    _name = "report.lighting_export_xlsx.export_product_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Export Product XLSX"

    def get_workbook_options(self):
        return {"strings_to_urls": False}

    def generate_xlsx_report(self, workbook, data, objects):
        self.with_context(lang=data["lang"]).generate_xlsx_report_ctx(
            workbook, data, objects
        )

    def generate_xlsx_report_ctx(self, workbook, data, objects):  # noqa: C901
        template_id = self.env["lighting.export.template"].browse(
            data.get("template_id")
        )

        if data.get("interval") == "all":
            active_model = self.env.context.get("active_model")
            active_domain = data.get("context").get("active_domain")
            objects = self.env[active_model].search(active_domain)
        else:
            objects = self.env["lighting.product"].browse(data.get("active_ids"))
        if data.get("exclude_configurator"):
            objects = objects.filtered(lambda x: not x.configurator)

        # base headers with labels replaced and subset acoridng to template
        header = []
        for line in template_id.field_ids.sorted(lambda x: x.sequence):
            item = objects.fields_get([line.field_id.name], ["type", "selection"])
            if item:
                field, meta = tuple(item.items())[0]
                # fields_get follows base_field for _inherits delegated fields,
                # returning the parent model's label instead of the current one.
                # Use line.field_id.field_description to get the correct label.
                if line.label and line.label.strip():
                    meta["string"] = line.label
                else:
                    meta["string"] = line.field_id.field_description
                meta.update(dict(num=0, subfields=None))
                header.append((field, meta))

        self._check_duplicate_labels(header, template_id)

        # generate data and gather header data
        objects_ld = self._generate_products(header, objects.ids, template_id)

        # generate xlsx headers according to data
        xlsx_header = []
        for _field, meta in header:
            if not meta["num"] and data.get("hide_empty_fields"):
                continue
            if not meta["subfields"]:
                xlsx_header.append(meta["string"])
            else:
                for sf in meta["subfields"]:
                    xlsx_header.append(sf)

        # write to xlsx
        sheet = workbook.add_worksheet(template_id.display_name)
        row = col = 0

        # write header to xlsx
        bold = workbook.add_format({"bold": True})
        for col_header in xlsx_header:
            sheet.write(row, col, col_header, bold)
            col += 1

        # returns a callable that maps field types to Excel cell formats
        cell_format = self._get_cell_format(workbook, data["lang"])

        # write data to xlsx
        row = 1
        for obj in objects_ld:
            col = 0
            for _field, meta in header:
                if not meta["num"] and data.get("hide_empty_fields"):
                    continue

                fmt = cell_format(meta["type"])
                if not meta["subfields"]:
                    value = obj[meta["string"]]
                    if fmt and value is not None:
                        sheet.write_datetime(row, col, value, fmt)
                    else:
                        sheet.write(row, col, value)
                    col += 1
                else:
                    for k in meta["subfields"]:
                        value = obj.get(k)
                        if fmt and value is not None:
                            sheet.write_datetime(row, col, value, fmt)
                        else:
                            sheet.write(row, col, value)
                        col += 1
            row += 1

    def _check_duplicate_labels(self, header, template_id):
        seen_labels = {}
        for field, meta in header:
            seen_labels.setdefault(meta["string"], []).append(field)
        duplicates = {
            label: fields for label, fields in seen_labels.items() if len(fields) > 1
        }
        if duplicates:
            details = "\n".join(
                _(
                    "- Column '%(label)s': fields %(fields)s",
                    label=label,
                    fields=", ".join(fields),
                )
                for label, fields in duplicates.items()
            )
            label_string = self.env["lighting.export.template.field"].fields_get(
                ["label"]
            )["label"]["string"]
            raise ValidationError(
                _(
                    "Cannot export template '%(template)s':"
                    " the following fields share the same column name"
                    " and would produce duplicate columns in the file."
                    "\n\n%(details)s"
                    "\n\nTo fix this, go to Export > Templates > %(template)s"
                    " and either:"
                    "\n- Remove one of the duplicated fields."
                    "\n- Set a different '%(label_field)s' on one of them.",
                    template=template_id.display_name,
                    details=details,
                    label_field=label_string,
                )
            )

    @staticmethod
    def _strftime_to_excel(fmt):
        return (
            fmt.replace("%d", "dd")
            .replace("%m", "mm")
            .replace("%Y", "yyyy")
            .replace("%y", "yy")
            .replace("%H", "hh")
            .replace("%M", "mm")
            .replace("%S", "ss")
        )

    def _get_cell_format(self, workbook, lang_code):
        lang = self.env["res.lang"]._lang_get(lang_code)
        xl_date = self._strftime_to_excel(lang.date_format)
        xl_time = self._strftime_to_excel(lang.time_format)
        formats = {
            "date": workbook.add_format({"num_format": xl_date}),
            "datetime": workbook.add_format(
                {"num_format": "%s %s" % (xl_date, xl_time)}
            ),
        }
        return lambda field_type: formats.get(field_type)

    def _get_meta_num(self, meta, datum, obj_d):
        subfields = []
        for j, sf in enumerate(datum, 1):
            # update x in headers
            sf1 = list(sf.keys())
            if subfields:
                if set(subfields) != set(sf1):
                    raise Exception("Unexpected Error")
            else:
                subfields = sf1

            fnam = "%s%i" % (meta["string"], j)
            for k, v in sf.items():
                sfkey = "%s/%s" % (fnam, k)
                if sfkey in obj_d:
                    raise Exception("The subfield '%s' is duplicated" % sfkey)
                obj_d[sfkey] = v

                if not meta["subfields"]:
                    meta["subfields"] = []
                if sfkey not in meta["subfields"]:
                    meta["subfields"].append(sfkey)

        return max(meta["num"], len(datum)), obj_d

    def _convert_field_value(self, obj, field, meta, template_id):
        datum = getattr(obj, field)
        if meta["type"] == "selection":
            datum = dict(meta["selection"]).get(datum)
        elif meta["type"] == "many2many":
            datum = ",".join([x.display_name for x in datum])
        elif meta["type"] == "boolean":
            datum = _("Yes") if datum else _("No")
        elif meta["type"] == "many2one":
            datum = datum.display_name
        elif meta["type"] == "one2many":
            if hasattr(datum, "export_xlsx"):
                datum = datum.export_xlsx(template_id)
            else:
                datum = None  # NOT SUPPORTED
        elif meta["type"] == "datetime":
            if datum:
                datum = fields.Datetime.context_timestamp(obj, datum)
                datum = datum.replace(tzinfo=None)
        elif meta["type"] == "serialized":
            datum = json.dumps(datum) if datum else None
        elif meta["type"] == "binary":
            datum = human_size(len(datum)) if datum else None
        if meta["type"] != "boolean" and not datum:
            datum = None
        return datum

    def _generate_products(self, header, object_ids, template_id):
        n = len(object_ids)
        _logger.info("Generating %i products..." % n)
        th = int(n / 100) or 1
        batch_size = template_id.export_batch_size
        objects_ld = []
        for batch_start in range(0, n, batch_size):
            batch_ids = object_ids[batch_start : batch_start + batch_size]
            batch = self.env["lighting.product"].browse(batch_ids)
            for i, obj in enumerate(batch, batch_start + 1):
                obj_d = {}
                for field, meta in header:
                    datum = self._convert_field_value(obj, field, meta, template_id)

                    if isinstance(datum, (tuple, list)):
                        meta["num"], obj_d = self._get_meta_num(meta, datum, obj_d)
                    else:
                        fkey = meta["string"]
                        if fkey in obj_d:
                            raise Exception("The field '%s' is duplicated" % fkey)
                        obj_d[fkey] = datum

                        if not meta["num"] and datum:
                            meta["num"] = 1

                objects_ld.append(obj_d)

                if (i % th) == 0:
                    _logger.info(
                        " - Progress products generation %i%%" % round(i / n * 100)
                    )
            batch.invalidate_recordset()

        _logger.info("Products successfully generated...")

        return objects_ld
