# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class BaseLightingSAPB1Connector(AbstractComponent):
    _name = "base.lighting.sapb1.connector"
    _inherit = "base.connector"
    _collection = "lighting.sapb1.backend"

    _description = "Base Lighting SAPB1 Connector Component"
