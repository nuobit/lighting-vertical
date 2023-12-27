# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingETIMClassSynonim(models.Model):
    _name = "lighting.etim.class.synonim"

    name = fields.Char(
        string="Synonim",
        required=True,
        translate=True,
    )

    class_id = fields.Many2one(
        comodel_name="lighting.etim.class",
        ondelete="cascade",
    )
