# Copyright 2021 Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class SapB1BackendLangMap(models.Model):
    _name = "sapb1.backend.lang.map"

    backend_id = fields.Many2one(
        comodel_name="sapb1.backend",
        required=True,
        ondelete="cascade",
    )

    lang_id = fields.Many2one(
        comodel_name='res.lang',
        string="Odoo Language",
        required=True,
        ondelete='restrict',
    )

    sap_lang_id = fields.Integer(
        string="SAP Language ID",
        required=True,
    )

    sap_main_lang = fields.Boolean('SAP Main Language')

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
