# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    def name_get(self):
        res = []
        for field in self:
            res.append((field.id, "%s" % (field.field_description,)))
        return res
