# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

import logging

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    _logger.info("Start: Delete records related with lighting.product.flux")

    env.cr.execute(
        """
        DROP TABLE lighting_product_advanced_search_flux_in_rel;
        """
    )

    _logger.info("End: Finish deletion of records related with lighting.product.flux")
