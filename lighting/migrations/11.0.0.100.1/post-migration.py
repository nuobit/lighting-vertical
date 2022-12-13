# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

import logging

from odoo.exceptions import ValidationError

# from odoo import _

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    _logger.info("Start moving lamp_included_efficiency_ids to efficiency_ids")
    lamp_included_eff = env['lighting.product.source.line'].search([('lamp_included_efficiency_ids', '!=', False)])
    # eff_and_lamp = source_line_temp_flux.filtered(lambda x: x.efficiency_ids and x.lamp_included_efficiency_ids)
    a = 1
    lamp_and_eff_same = lamp_included_eff.filtered(lambda x: x.lamp_included_efficiency_ids == x.efficiency_ids)
    lamp_and_not_eff = lamp_included_eff.filtered(lambda x: not x.efficiency_ids)
    lamp_and_eff_diff = lamp_included_eff.filtered(
        lambda x: x.efficiency_ids and x.lamp_included_efficiency_ids != x.efficiency_ids)
    a = 1
    for rec in lamp_and_eff_diff:
        if not rec.source_id.product_id.is_accessory:
            print("NO ES ACCESORIO --> ", rec.source_id.product_id)
        if rec.source_id.product_id.is_accessory:
            rec.efficiency_ids |= rec.lamp_included_efficiency_ids
        # raise ValidationError("Review this products:%s" % lamp_and_eff_diff.mapped('source_id.product_id'))
        a = 1
    for rec in lamp_and_not_eff:
        # raise ValidationError("ERROR, don't write fields yet")
        rec.efficiency_ids = rec.lamp_included_efficiency_ids
        raise ValidationError("ERROR, don't unlink yet")
        rec.lamp_included_efficiency_ids.unlink()
    for rec in lamp_and_eff_same:
        raise ValidationError("ERROR, don't unlink yet")
        rec.lamp_included_efficiency_ids.unlink()
        _logger.info("End setting efficiencies in lighting product source line CCTs")
