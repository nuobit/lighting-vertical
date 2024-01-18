# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class LightingSAPB1ProductBinding(models.Model):
    _name = "lighting.sapb1.product"
    _inherit = "lighting.sapb1.binding"
    _inherits = {"lighting.product": "odoo_id"}
    _description = "Lighting SAP B1 Lighting product Binding"

    odoo_id = fields.Many2one(
        comodel_name="lighting.product",
        string="Product",
        required=True,
        ondelete="cascade",
    )
    sapb1_idproduct = fields.Char(
        string="SAP B1 ID Product",
        readonly=True,
    )

    _sql_constraints = [
        (
            "external_uniq",
            "unique(backend_id, sapb1_idproduct)",
            "A binding already exists with the same External (idProduct) ID.",
        ),
    ]

    @api.model
    def _get_base_domain(self):
        return []

    # @job(default_channel="root.sapb1.lighting")
    def import_products_since(self, backend_record=None, since_date=None):
        """Prepare the batch import of products modified on SAP B1 Lighting"""
        domain = self._get_base_domain()
        existing_hashes = (
            self.env["lighting.sapb1.product"]
            .search([])
            .mapped("external_content_hash")
        )
        if existing_hashes:
            domain += [("Hash", "not in", existing_hashes)]
        #     TODO: NEW: How can we import with date?
        # if since_date:
        #     domain += [("after", "=", since_date)]
        # now_fmt = fields.Datetime.now()
        self.import_batch(backend_record, domain=domain, use_data=False)
        # backend_record.import_products_since_date = now_fmt
        return True

    # @job(default_channel="root.sapb1.lighting")
    def export_products_since(self, backend_record=None, since_date=None):
        """Prepare the batch export of products modified on Odoo"""
        domain = self._get_base_domain()
        if since_date:
            domain += [
                ("sapb1_write_date", ">", fields.Datetime.to_datetime(since_date)),
            ]
        self.export_batch(backend_record, domain=domain)
