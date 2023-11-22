# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    openupgrade.rename_fields(
        env,
        [
            ("lighting.product", "lighting_product", "odoo_id", "odoop_id"),
        ],
    )
    env.cr.execute(
        """
        ALTER TABLE lighting_product
        RENAME CONSTRAINT lighting_product_odoo_id_fkey
        TO lighting_product_odoop_id_fkey
    """
    )
