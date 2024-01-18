# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class SAPB1LightingBaseConnectorComponent(AbstractComponent):
    """Base SAP B1 Lighting Connector Component

    All components of this connector should inherit from it.
    """

    _name = "base.sapb1.lighting.connector"
    _inherit = "base.connector"
    _collection = "sapb1.lighting.backend"
