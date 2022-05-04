# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class SAPB1LightingExportMapper(AbstractComponent):
    _name = 'sapb1.lighting.export.mapper'
    _inherit = ['base.export.mapper', 'base.sapb1.lighting.connector']


class SAPB1LightingExportMapChild(AbstractComponent):
    _name = 'sapb1.lighting.map.child.export'
    _inherit = ['base.map.child.export', 'base.sapb1.lighting.connector']
