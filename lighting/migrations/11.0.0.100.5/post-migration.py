# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    _logger.info(
        "Start: Moving total_nominal_flux from lighting_product to lighting_product_source_line_color_temperature_flux")

    env.cr.execute("""
        update lighting_product_source_line_color_temperature_flux ctf
        set total_flux = p.total_nominal_flux
        from lighting_product_source_line l, lighting_product_source s, lighting_product p
        where ctf.source_line_id = l.id and
              l.source_id = s.id and
              p.id = s.product_id
    """)

    _logger.info("End: FINISH")
