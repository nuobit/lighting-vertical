# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    # recalculate automatic descriptions
    _logger.info("Recalculating descriptions...")
    for p in env["lighting.product"].search([]):
        p._update_computed_description()
    _logger.info("Descriptions successfully recalculated")
