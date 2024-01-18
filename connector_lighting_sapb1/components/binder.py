# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class LightingSAPB1ModelBinder(AbstractComponent):
    """Bind records and give odoo/sapb1 ids correspondence

    Binding models are models called ``lighting.sapb1.{normal_model}``,
    like ``lighting.sapb1.product``.
    They are ``_inherits`` of the normal models and contains
    the SAP B1 ID, the ID of the SAP B1 Backend and the additional
    fields belonging to the SAP B1 instance.
    """

    _name = "lighting.sapb1.binder"
    _inherit = ["connector.extension.generic.binder", "base.lighting.sapb1.connector"]

    _bind_ids_field = "sapb1_lighting_bind_ids"
