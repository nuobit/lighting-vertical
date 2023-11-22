# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    _logger.info("Removing efficiency ids when lines are informed")
    env["lighting.product.source.line.color.temperature.flux"].search(
        [("efficiency_id", "!=", False)]
    ).mapped("source_line_id").write(
        {
            "efficiency_ids": [(5,)],
        }
    )
    _logger.info("Removed efficiency ids!")
