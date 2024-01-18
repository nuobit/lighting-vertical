# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class LightingSAPB1ExportMapper(AbstractComponent):
    _name = "lighting.sapb1.export.mapper"
    _inherit = ["connector.extension.export.mapper", "base.lighting.sapb1.connector"]


class LightingSAPB1ExportMapChild(AbstractComponent):
    _name = "lighting.sapb1.map.child.export"
    _inherit = ["connector.extension.map.child.export", "base.lighting.sapb1.connector"]
