# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class LightingBMEcatPackingUnit(models.Model):
    _name = "lighting.bmecat.packing.unit"
    _description = "Lighting BMEcat Packing Unit"

    code = fields.Char(required=True)
    name = fields.Char(required=True)
