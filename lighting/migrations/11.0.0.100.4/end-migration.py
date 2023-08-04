# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

import logging

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    _logger.info("Start: Delete all records related with lighting.product.flux")

    openupgrade.drop_columns(
        env.cr,
        [('lighting_product_source_line_color_temperature_flux', 'flux_id'), ]
    )

    env.cr.execute(
        """
        DROP TABLE lighting_product_flux;
        """
    )

    env.cr.execute(
        """
        DELETE FROM ir_model WHERE model = 'lighting.product.flux';
        """
    )

    _logger.info("End: Finish deletion of all records related with lighting.product.flux")
