# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions 2025 - Bijaya Kumal <bkumal@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class LightingETIMClassSynonim(models.Model):
    _name = "lighting.etim.class.synonim"
    _description = "ETIM Class Synonim"

    name = fields.Char(
        string="Synonim",
        required=True,
        translate=True,
    )

    class_id = fields.Many2one(
        comodel_name="lighting.etim.class",
        ondelete="cascade",
    )
