# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    env["lighting.product.special.spectrum"].with_context(lang="en_US").search(
        [("name", "in", ("TW", "DtW"))],
    ).write({"use_as_cct": True})

    _logger.info("Updated use_as_ctt record.")
