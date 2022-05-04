# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SapB1BackendCatalogMap(models.Model):
    _name = "sapb1.lighting.backend.catalog.map"

    backend_id = fields.Many2one(
        comodel_name="sapb1.lighting.backend",
        required=True,
        ondelete="cascade",
    )

    catalog_id = fields.Many2one(
        comodel_name='lighting.catalog',
        string="Odoo Catalog",
        required=True,
        ondelete='restrict',
    )

    sap_item_group_id = fields.Integer(
        string="SAP Item Group ID",
        required=True,
    )

    _sql_constraints = [
        (
            "uniq",
            "unique(backend_id,catalog_id,sap_item_group_id)",
            "Catalog mapping ling duplicated",
        ),
        (
            "catalog_uniq",
            "unique(backend_id,catalog_id)",
            "Odoo Catalog used in another map line",
        ),
        (
            "sap_item_group_code_uniq",
            "unique(backend_id,sap_item_group_id)",
            "SAP Item Group ID used in another map line",
        ),
    ]
