# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class LightingSapB1BackendLangMap(models.Model):
    _name = "lighting.sapb1.backend.lang.map"
    _description = "Lighting SAP B1 Backend Lang Map"

    backend_id = fields.Many2one(
        comodel_name="lighting.sapb1.backend",
        required=True,
        ondelete="cascade",
    )
    lang_id = fields.Many2one(
        comodel_name="res.lang",
        string="Odoo Language",
        required=True,
        ondelete="restrict",
    )
    sap_lang_id = fields.Integer(
        string="SAP Language ID",
        required=True,
    )
    sap_main_lang = fields.Boolean(
        string="SAP Main Language",
    )

    _sql_constraints = [
        (
            "uniq",
            "unique(backend_id,lang_id,sap_lang_id)",
            "Language mapping ling duplicated",
        ),
        (
            "catalog_uniq",
            "unique(backend_id,lang_id)",
            "Odoo Language used in another map line",
        ),
        (
            "sap_item_group_code_uniq",
            "unique(backend_id,sap_lang_id)",
            "SAP Language ID used in another map line",
        ),
    ]
