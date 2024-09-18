# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class LightingProduct(models.Model):
    _inherit = "lighting.product"

    def get_finish_display(self):
        self.ensure_one()
        res, res_l = None, []

        # add finish description
        finish_l = []
        if self.finish_id:
            finish_l.append(self.finish_id.display_name)
        if self.finish2_id:
            finish_l.append(self.finish2_id.display_name)
        if finish_l:
            res_l.append("/".join(finish_l))

        # add RAL description
        if self.ral_id:
            res_l.append("(%s)" % self.ral_id.display_name)

        if res_l:
            res = " ".join(res_l)

        return res
