# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class SAPB1LightingLightingImportMapper(AbstractComponent):
    _name = "sapb1.lighting.import.mapper"
    _inherit = ["base.import.mapper", "base.sapb1.lighting.connector"]


class SAPB1LightingImportMapChild(AbstractComponent):
    _name = "sapb1.lighting.map.child.import"
    _inherit = ["base.map.child.import", "base.sapb1.lighting.connector"]
