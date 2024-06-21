# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    product_template = (
        env["ir.config_parameter"]
        .sudo()
        .get_param("lighting_reporting_product.product_template")
    )
    if not product_template:
        env["ir.config_parameter"].sudo().set_param(
            "lighting_reporting_product.product_template", "vanguard"
        )
