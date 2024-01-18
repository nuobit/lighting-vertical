# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class LightingSAPB1BackendAdapter(Component):
    _name = "connector.lighting.sapb1.backend.adapter"
    _inherit = "connector.lighting.sapb1.adapter"
    _description = "Lighting SAPB1 Backend Adapter"

    _apply_on = "lighting.sapb1.backend"
