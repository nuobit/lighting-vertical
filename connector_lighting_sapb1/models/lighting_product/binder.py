# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class LightingProductBinder(Component):
    """Bind records and give odoo/sapbb1 ids correspondence

    Binding models are models called ``sapb1.lighting.{normal_model}``,
    like ``sapb1.lighting.product``.
    They are ``_inherits`` of the normal models and contains
    the SAP B1 Lighting ID, the ID of the SAP B1 Lighting Backend and the additional
    fields belonging to the SAP B1 instance.
    """

    _name = "sapb1.lighting.product.binder"
    _inherit = "sapb1.lighting.binder"

    _apply_on = "sapb1.lighting.product"
