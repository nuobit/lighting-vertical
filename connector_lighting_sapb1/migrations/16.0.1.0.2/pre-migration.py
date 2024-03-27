# Copyright 2024 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE lighting_sapb1_product l
        SET sapb1_idproduct = substring(l.external_id, 3, LENGTH(l.external_id) - 4)
        """,
    )
