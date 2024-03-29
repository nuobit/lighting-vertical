# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import fields, models

from odoo.addons.lighting.models.product import STATES_MARKETING

_logger = logging.getLogger(__name__)


class LightingSapB1BackendStateMarketingMap(models.Model):
    _name = "lighting.sapb1.backend.state.marketing.map"
    _description = "Lighting SAP B1 Backend State Marketing Map"

    backend_id = fields.Many2one(
        comodel_name="lighting.sapb1.backend",
        required=True,
        ondelete="cascade",
    )
    state_marketing = fields.Selection(
        string="Odoo State Marketing",
        required=True,
        selection=STATES_MARKETING,
    )
    sap_state_reference = fields.Char(
        string="SAP State Reference",
        required=True,
    )

    _sql_constraints = [
        (
            "uniq",
            "unique(backend_id,state_marketing,sap_state_reference)",
            "State Marketing mapping ling duplicated",
        ),
        (
            "state_marketing_uniq",
            "unique(backend_id,state_marketing)",
            "Odoo State Marketing used in another map line",
        ),
        (
            "ssr_uniq",
            "unique(backend_id,sap_state_reference)",
            "SAP State Marketing already used in another map line",
        ),
    ]
