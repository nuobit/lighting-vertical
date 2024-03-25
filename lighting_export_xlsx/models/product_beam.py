# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from collections import OrderedDict

from odoo import api, fields, models


class LightingProductBeam(models.Model):
    _inherit = "lighting.product.beam"

    @property
    def xlsx_dimensions(self):
        field = "dimension_ids"
        meta = self.env[self._name].fields_get([field], ["string"])[field]
        datum = self.dimension_ids.get_display()
        return {meta["string"]: datum or None}

    @api.multi
    def export_xlsx(self, template_id=None):
        valid_field = ["num", "photometric_distribution_ids", "xlsx_dimensions"]

        field_meta_base = self.fields_get(valid_field, ["string", "type", "selection"])
        res = []
        for rec in self.sorted(lambda x: x.sequence):
            line = OrderedDict()
            for field in valid_field:
                datum = getattr(rec, field)
                if field in field_meta_base:
                    field_meta = field_meta_base[field]
                else:
                    field_meta = {
                        "type": None,
                        "string": list(datum.keys())[0],
                    }
                    datum = list(datum.values())[0]
                if field_meta["type"] == "selection":
                    datum = dict(field_meta["selection"]).get(datum)
                elif field_meta["type"] == "many2one":
                    datum = datum.display_name
                elif field_meta["type"] == "many2many":
                    datum = ",".join([x.display_name for x in datum])
                elif field_meta["type"] == "date":
                    datum = fields.Date.from_string(datum)

                if field_meta["type"] != "boolean" and not datum:
                    datum = None

                if not isinstance(datum, OrderedDict):
                    datum = OrderedDict([(field_meta["string"], datum)])

                line.update(datum)

            res.append(line)

        return res
