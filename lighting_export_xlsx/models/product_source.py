# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from collections import OrderedDict

from odoo import _, api, fields, models


class LightingProductSource(models.Model):
    _inherit = "lighting.product.source"

    @property
    def xlsx_types(self):
        SourceLine = self.env[self._name].line_ids
        field = "type_id"
        meta = SourceLine.fields_get([field], ["string"])[field]
        datum = self.line_ids.get_source_type()
        return {meta["string"]: datum and "/".join(datum) or None}

    @property
    def xlsx_wattage(self):
        SourceLine = self.env[self._name].line_ids
        field = "wattage"
        meta = SourceLine.fields_get([field], ["string"])[field]
        datum = self.line_ids.get_wattage()
        return {meta["string"]: datum or None}

    @property
    def xlsx_color_temperature(self):
        datum = self.line_ids.get_color_temperature()
        return {_("Color temperature"): datum and ", ".join(datum) or None}

    @property
    def xlsx_cri(self):
        SourceLine = self.env[self._name].line_ids
        field = "cri_min"
        meta = SourceLine.fields_get([field], ["string"])[field]
        cri_l = self.line_ids.get_cri()
        if cri_l:
            datum = [str(x) for x in cri_l if x]
        else:
            datum = None
        return {meta["string"]: datum and ", ".join(datum) or None}

    @property
    def xlsx_luminous_flux(self):
        datum = self.line_ids.get_luminous_flux()
        return {_("Flux"): datum and ", ".join(datum) or None}

    @property
    def xlsx_energy_efficiency(self):
        datum = self.line_ids.get_energy_efficiency()
        return {_("Energy Efficiency"): datum and ", ".join(datum) or None}

    @api.multi
    def export_xlsx(self, template_id=None):
        valid_field = [
            "relevance",
            "num",
            "lampholder_id",
            "xlsx_types",
            "xlsx_wattage",
            "xlsx_color_temperature",
            "xlsx_luminous_flux",
            "xlsx_cri",
            "xlsx_energy_efficiency",
        ]

        field_meta_base = self.fields_get(valid_field, ["string", "type", "selection"])
        res = []
        for rec in self.sorted(lambda x: x.sequence):
            line = OrderedDict()
            for field in valid_field:
                datum = getattr(rec, field)
                if field in field_meta_base:
                    field_meta = field_meta_base[field]
                else:
                    try:
                        field_meta = {
                            "type": None,
                            "string": list(datum.keys())[0],
                        }
                    except:
                        raise
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
