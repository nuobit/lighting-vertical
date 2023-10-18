# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    openupgrade.drop_columns(
        env.cr,
        [('lighting_product_source_line', 'special_spectrum'),
         ]
    )

    _logger.info("End: Removed special spectrum from product source line")


