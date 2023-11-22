# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    _logger.info("Start moving lamp_included_efficiency_ids to efficiency_ids")

    env.cr.execute(
        """INSERT INTO lighting_product_source_energyefficiency_rel (lighting_product_source_line_id,
        lighting_energyefficiency_id)
        SELECT lighting_product_source_line_id,lighting_energyefficiency_id
        FROM lighting_product_source_lampenergyefficiency_rel l
        WHERE NOT EXISTS (
           SELECT 1
           FROM lighting_product_source_energyefficiency_rel e
           WHERE e.lighting_product_source_line_id = l.lighting_product_source_line_id AND
           e.lighting_energyefficiency_id = l.lighting_energyefficiency_id
        )"""
    )
