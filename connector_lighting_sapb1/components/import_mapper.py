# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class LightingSAPB1ImportMapper(AbstractComponent):
    _name = "lighting.sapb1.import.mapper"
    _inherit = ["connector.extension.import.mapper", "base.lighting.sapb1.connector"]


class LightingSAPB1ImportMapChild(AbstractComponent):
    _name = "lighting.sapb1.map.child.import"
    _inherit = ["connector.extension.map.child.import", "base.lighting.sapb1.connector"]
