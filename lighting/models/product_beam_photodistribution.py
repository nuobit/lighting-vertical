# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class LightingProductBeamPhotometricDistribution(models.Model):
    _name = "lighting.product.beam.photodistribution"
    _order = "name"

    name = fields.Char(string="Description", required=True, translate=True)

    color = fields.Integer(string="Color Index")

    _sql_constraints = [
        (
            "name_uniq",
            "unique (name)",
            "The photometric distribution name must be unique!",
        ),
    ]

    @api.multi
    def unlink(self):
        records = self.env["lighting.product"].search(
            [("photometric_distribution_ids", "in", self.ids)]
        )
        if records:
            raise UserError(
                _("You are trying to delete a record that is still referenced!")
            )
        return super(LightingProductBeamPhotometricDistribution, self).unlink()
