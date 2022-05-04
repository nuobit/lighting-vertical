# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)



def migrate(cr, version):
    if not version:
        return

    ### rename model
    openupgrade.rename_models(
        cr, [('sapb1.lighting.product', 'sapb1.light.product'),
        ]
    )

    ### rename DB
    # rename table and sequence
    openupgrade.rename_tables(
        cr, [('sapb1_lighting_product', 'sapb1_light_product')]
    )
