# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    openupgrade.m2o_to_x2m(
        env.cr,
        env['lighting.product'],
        'lighting_product',
        'type_ids',
        openupgrade.get_legacy_name('type_id'),
    )