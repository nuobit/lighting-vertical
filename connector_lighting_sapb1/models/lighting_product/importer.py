# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class LightingProductImporter(Component):
    _name = "sapb1.lighting.product.importer"
    _inherit = "sapb1.lighting.importer"

    _apply_on = "sapb1.lighting.product"

    def _find_existing(self, external_id):
        """Find existing record by external_id"""
        adapter = self.component(usage="backend.adapter", model_name=self.model)
        external_id_d = adapter.id2dict(external_id)

        reference = external_id_d["ItemCode"]
        if reference:
            product = self.env["lighting.product"].search(
                [
                    ("reference", "=", reference),
                ]
            )
            if product:
                if len(product) > 1:
                    raise Exception(
                        "There's more than one existing product "
                        "with the same Reference %s" % reference
                    )
                return {
                    "odoo_id": product.id,
                }

        return None

    def _mapper_options(self, binding):
        return {"binding": binding}


class LightingProductDirectBatchImporter(Component):
    """Import the SAP B1 Lighting Products.

    For every product in the list, import it directly.
    """

    _name = "sapb1.lighting.product.direct.batch.importer"
    _inherit = "sapb1.lighting.direct.batch.importer"

    _apply_on = "sapb1.lighting.product"


class LightingProductDelayedBatchImporter(Component):
    """Import the SAP B1 Lighting Products.

    For every product in the list, a delayed job is created.
    """

    _name = "sapb1.lighting.product.delayed.batch.importer"
    _inherit = "sapb1.lighting.delayed.batch.importer"

    _apply_on = "sapb1.lighting.product"
