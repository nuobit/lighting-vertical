# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from collections import OrderedDict, defaultdict

from odoo import models


class LightingAttachment(models.Model):
    _inherit = "lighting.attachment"

    def export_xlsx(self, template_id=None):
        res = OrderedDict()
        type_count = defaultdict(int)
        for ta in template_id.attachment_ids.sorted(lambda x: x.sequence):
            prod_attachment_ids = self.filtered(lambda x: x.type_id.id == ta.type_id.id)
            if prod_attachment_ids.mapped("attachment_id"):
                non_public = prod_attachment_ids.filtered(lambda x: not x.public)
                if non_public:
                    self.env.context["non_public_attachment_ids"].extend(non_public.ids)
                for pa in prod_attachment_ids:
                    if not pa.attachment_id:
                        continue
                    type_name = pa.type_id.display_name
                    type_count[type_name] += 1
                    key = "%s %d" % (type_name, type_count[type_name])
                    res[key] = pa.url_get(resolution=ta.resolution)
        return res
