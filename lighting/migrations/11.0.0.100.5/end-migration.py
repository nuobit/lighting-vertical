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
        [('lighting_product', 'total_nominal_flux')]
    )

    _logger.info("End: Removed total_nominal_flux and the dependent views")
