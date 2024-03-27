# Copyright 2024 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not version:
        return
    openupgrade.drop_columns(
        env.cr,
        [
            ("lighting_sapb1_product", "external_id"),
            ("lighting_sapb1_product", "external_id_hash"),
        ],
    )
