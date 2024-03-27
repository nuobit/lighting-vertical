# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class LightingSAPB1Binding(models.AbstractModel):
    _name = "lighting.sapb1.binding"
    _inherit = "connector.extension.external.binding"
    _description = "SAP B1 Lighting Binding (abstract)"

    backend_id = fields.Many2one(
        comodel_name="lighting.sapb1.backend",
        string="SAP B1 Lighting Backend",
        required=True,
        readonly=True,
        ondelete="restrict",
    )

    external_content_hash = fields.Char(
        string="SAP content hash",
        required=True,
    )

    _sql_constraints = [
        (
            "sapb1_odoo_uniq",
            "unique(backend_id, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
    ]
