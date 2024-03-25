# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from collections import OrderedDict

from odoo import api, models


class LightingAttachment(models.Model):
    _inherit = "lighting.attachment"

    @api.multi
    def export_xlsx(self, template_id=None):
        res = []
        for ta in template_id.attachment_ids.sorted(lambda x: x.sequence):
            prod_attachment_ids = self.filtered(lambda x: x.type_id.id == ta.type_id.id)
            if prod_attachment_ids.mapped("attachment_id"):
                for pa in prod_attachment_ids:
                    if not pa.public:
                        pa.sudo().public = True
                    type_meta = pa.fields_get(["type_id"], ["string"])["type_id"]
                    res.append(
                        OrderedDict(
                            [
                                (type_meta["string"], pa.type_id.display_name),
                                ("URL", pa.url_get(resolution=ta.resolution)),
                            ]
                        )
                    )
        return res
