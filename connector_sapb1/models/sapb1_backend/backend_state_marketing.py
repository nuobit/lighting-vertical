# Copyright 2021 Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import fields, models
from odoo.addons.lighting.models.product import STATES_MARKETING

_logger = logging.getLogger(__name__)


class SapB1BackendStateMarketingMap(models.Model):
    _name = "sapb1.backend.state.marketing.map"

    backend_id = fields.Many2one(
        comodel_name="sapb1.backend",
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
            "sap_state_reference_uniq",
            "unique(backend_id,sap_state_reference)",
            "SAP State Marketing already used in another map line",
        ),
    ]
