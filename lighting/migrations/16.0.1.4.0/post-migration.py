# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        "DROP TABLE IF EXISTS lighting_product_spare_part_rel",
    )
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE lighting_product_category " "DROP COLUMN IF EXISTS is_component",
    )
