# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    _logger.info("Start: Pass the flux_id from a Many2one to a float")

    env.cr.execute(
        """
        UPDATE lighting_product_source_line_color_temperature_flux
        SET nominal_flux = lpf.value::float8
        FROM lighting_product_flux lpf
        WHERE lighting_product_source_line_color_temperature_flux.flux_id = lpf.id
        """
    )

    _logger.info("End: Finish flux_id pass")
