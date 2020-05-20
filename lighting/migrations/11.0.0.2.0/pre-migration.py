# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    ### rename manual description
    openupgrade.rename_fields(
        env, [('lighting.product', 'lighting_product',
               'description', 'description_manual'),
        ]
    )

    env.cr.execute(
        "COMMENT ON COLUMN lighting_product.description_manual "
        "IS 'Description (manual)'"
    )
