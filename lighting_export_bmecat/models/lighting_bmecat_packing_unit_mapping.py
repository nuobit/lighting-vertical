# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class LightingBMEcatPackingUnitMapping(models.Model):
    _name = "lighting.bmecat.packing.unit.mapping"
    _description = "Lighting BMEcat Packing Unit Mapping"

    config_id = fields.Many2one(
        comodel_name="lighting.bmecat.config",
        required=True,
        ondelete="cascade",
    )
    packing_unit_id = fields.Many2one(
        comodel_name="lighting.bmecat.packing.unit", required=True
    )
    uom_id = fields.Many2one(comodel_name="uom.uom", required=True)

    @api.constrains("uom_id")
    def _check_unique_uom_id(self):
        for rec in self:
            duplicate = self.search(
                [
                    ("config_id", "=", rec.config_id.id),
                    ("uom_id", "=", rec.uom_id.id),
                    ("id", "!=", rec.id),
                ]
            )
            if duplicate:
                raise ValidationError(
                    _(
                        "The same Unit of Measure (UoM) cannot be used "
                        "more than once in the same BMEcat."
                    )
                )
