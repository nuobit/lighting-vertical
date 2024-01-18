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

    # external_id = fields.Serialized(default=None)

    # external_id_display = fields.Char(
    #     string="SAP B1 Lighting ID",
    #     compute="_compute_external_id_display",
    #     search="_search_external_id_display",
    # )
    #
    # @api.depends("external_id")
    # def _compute_external_id_display(self):
    #     for rec in self:
    #         rec.external_id_display = (
    #             rec.external_id and json.dumps(rec.external_id) or None
    #         )
    #
    # # TODO: Try this list2hash
    # def _search_external_id_display(self, operator, value):
    #     return [
    #         (
    #             "external_id_hash",
    #             operator,
    #             value and list2hash(json.loads(value)) or None,
    #         )
    #     ]
    #
    # # Aquest camp s'utilitza per a fer una cerca
    # sense tenir guardat el display name a la bbdd??
    # external_id_hash = fields.Char(
    #     compute="_compute_external_id_hash",
    #     store=True,
    # )
    #
    # # TODO: Try this list2hash
    # @api.depends("external_id")
    # def _compute_external_id_hash(self):
    #     for rec in self:
    #         rec.external_id_hash = (
    #             rec.external_id and list2hash(rec.external_id) or None
    #         )
    #
    external_content_hash = fields.Char(
        string="SAP content hash",
        required=True,
    )

    _sql_constraints = [
        (
            "sapb1_external_uniq",
            "unique(backend_id, external_id_hash)",
            "An Odoo record with same ID already exists on SAP B1 Lighting.",
        ),
        (
            "sapb1_odoo_uniq",
            "unique(backend_id, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
    ]

    # @api.model
    # def import_batch(self, backend, filters=[]):
    #     """Prepare the batch import of records modified on SAP B1"""
    #     _logger.info("Start batch import of %s", self._name)
    #     with backend.work_on(self._name) as work:
    #         importer = work.component(usage="delayed.batch.importer")
    #         return importer.run(filters=filters)
    #     _logger.info("Finish batch import of %s", self._name)
    #
    # @api.model
    # def export_batch(self, backend, domain=[]):
    #     """Prepare the batch export of records modified on Odoo"""
    #     with backend.work_on(self._name) as work:
    #         exporter = work.component(usage="delayed.batch.exporter")
    #         return exporter.run(domain=domain)
    #
    # # TODO: define job in data file
    # # @job(default_channel="root.sapb1.lighting")
    # @api.model
    # def import_record(self, backend, external_id):
    #     """Import SAP B1 Lighting record"""
    #     with backend.work_on(self._name) as work:
    #         importer = work.component(usage="record.importer")
    #         return importer.run(external_id)
    #
    # # TODO: define job in data file
    # # @job(default_channel="root.sapb1.lighting")
    # @api.model
    # def export_record(self, backend, relation):
    #     """Export Odoo record"""
    #     with backend.work_on(self._name) as work:
    #         exporter = work.component(usage="record.exporter")
    #         return exporter.run(relation)
