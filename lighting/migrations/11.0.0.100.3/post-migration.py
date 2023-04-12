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
        "Start: removing content in color_temperature_flux_ids when is_integrated and is_lamp_included is false")
    env.cr.execute("""
        DELETE FROM lighting_product_source_line_color_temperature_flux ct 
        WHERE EXISTS ( SELECT 1 
        FROM lighting_product_source_line l, lighting_product_source_type t 
        WHERE l.id = ct.source_line_id AND l.type_id = t.id AND NOT t.is_integrated AND NOT l.is_lamp_included)
    """)
    _logger.info("End: removed content")
