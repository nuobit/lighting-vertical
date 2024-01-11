# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from collections import OrderedDict

from odoo import fields, models


class LightingProductSupplier(models.Model):
    _inherit = "lighting.product.supplier"

    def export_xlsx(self, template_id=None):
        valid_field = ["supplier_id", "reference"]
        res = []
        for rec in self.sorted(lambda x: x.sequence):
            line = OrderedDict()
            for field in valid_field:
                field_meta = self.fields_get([field], ["string", "type"])[field]
                datum = getattr(rec, field)
                if field_meta["type"] == "many2one":
                    datum = datum.display_name
                elif field_meta["type"] == "many2many":
                    datum = ",".join([x.display_name for x in datum])
                elif field_meta["type"] == "one2many":
                    datum = datum.export_xlsx()
                elif field_meta["type"] == "date":
                    datum = fields.Date.from_string(datum)

                if field_meta["type"] != "boolean" and not datum:
                    datum = None

                line[field_meta["string"]] = datum

            res.append(line)

        return res
