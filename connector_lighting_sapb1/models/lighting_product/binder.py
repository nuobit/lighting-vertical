# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class LightingProductBinder(Component):
    """Bind records and give odoo/sapbb1 ids correspondence

    Binding models are models called ``lighting.sapb1.{normal_model}``,
    like ``lighting.sapb1.product``.
    They are ``_inherits`` of the normal models and contains
    the SAP B1 Lighting ID, the ID of the SAP B1 Lighting Backend and the additional
    fields belonging to the SAP B1 instance.
    """

    _name = "lighting.sapb1.product.binder"
    _inherit = "lighting.sapb1.binder"

    _apply_on = "lighting.sapb1.product"

    external_id = "ItemCode"
    internal_id = "sapb1_idproduct"

    internal_alt_id = "reference"
