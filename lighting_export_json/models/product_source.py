# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields, _
from collections import OrderedDict

from .mixin import LightingExportJsonMixin


class LightingProductSource(models.Model, LightingExportJsonMixin):
    _inherit = 'lighting.product.source'

    @api.multi
    def export_json(self, template_id=None):
        valid_field = ['sequence', 'relevance', 'num', 'lampholder_id', 'line_ids']
        translate_field = ['relevance']
        res = []
        for rec in self.sorted(lambda x: x.sequence):
            line = OrderedDict()
            for field in valid_field:
                field_d = rec.get_field_d(field, template_id, translate=field in translate_field)

                if field_d:
                    line[field] = field_d

            if line:
                res.append(line)

        return res


class LightingProductSourceLine(models.Model, LightingExportJsonMixin):
    _inherit = 'lighting.product.source.line'

    @api.multi
    def export_json(self, template_id=None):
        valid_field = ['sequence', 'type_id', 'is_integrated', 'wattage', 'wattage_magnitude', 'is_max_wattage',
                       'is_lamp_included', 'color_temperature', 'luminous_flux1', 'luminous_flux2']
        translate_field = []
        res = []
        for rec in self.sorted(lambda x: x.sequence):
            line = OrderedDict()
            for field in valid_field:
                field_d = rec.get_field_d(field, template_id, translate=field in translate_field)

                if field_d:
                    line[field] = field_d

            if line:
                res.append(line)

        return res
