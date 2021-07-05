# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent
from odoo.addons.component_event import skip_if


class SAPB1Listener(AbstractComponent):
    _name = "sapb1.listener"
    _inherit = "base.connector.listener"
