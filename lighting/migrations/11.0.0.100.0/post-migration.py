# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from openupgradelib import openupgrade

# from odoo.exceptions import ValidationError
# from odoo import _

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    _logger.info("Start setting efficiencies in lighting product source line CCTs")
    source_line_temp_flux = env[
        "lighting.product.source.line.color.temperature.flux"
    ].search([("source_line_id.efficiency_ids", "!=", False)])
    # source_line_temp_flux_multiple = source_line_temp_flux.filtered(lambda x: len(x.source_line_id.efficiency_ids) > 1)
    # if source_line_temp_flux_multiple:
    #     raise ValidationError(
    #         _('More than one efficiency found in product: %s') %
    #         sorted(source_line_temp_flux_multiple.mapped('source_line_id.source_id.product_id.reference')))
    source_line_temp_flux_unique = source_line_temp_flux.filtered(
        lambda x: len(x.source_line_id.efficiency_ids) == 1
    )
    for line in source_line_temp_flux_unique.mapped("source_line_id"):
        line.color_temperature_flux_ids.write({"efficiency_id": line.efficiency_ids.id})
    _logger.info("End setting efficiencies in lighting product source line CCTs")
