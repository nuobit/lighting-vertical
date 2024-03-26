# Copyright 2024 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2024 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_model_renames = [
    ("sapb1.lighting.binding", "lighting.sapb1.binding"),
    ("sapb1.lighting.backend", "lighting.sapb1.backend"),
    ("sapb1.lighting.backend.catalog.map", "lighting.sapb1.backend.catalog.map"),
    ("sapb1.lighting.backend.lang.map", "lighting.sapb1.backend.lang.map"),
    (
        "sapb1.lighting.backend.state.marketing.map",
        "lighting.sapb1.backend.state.marketing.map",
    ),
    ("sapb1.lighting.product", "lighting.sapb1.product"),
]
_table_renames = [
    ("sapb1_lighting_backend", "lighting_sapb1_backend"),
    ("sapb1_lighting_backend_catalog_map", "lighting_sapb1_backend_catalog_map"),
    ("sapb1_lighting_backend_lang_map", "lighting_sapb1_backend_lang_map"),
    (
        "sapb1_lighting_backend_state_marketing_map",
        "lighting_sapb1_backend_state_marketing_map",
    ),
    ("sapb1_lighting_product", "lighting_sapb1_product"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE queue_job
        SET channel = 'root.lighting_sapb1'
        WHERE channel = 'root.sapb1.lighting'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE queue_job_function
        SET channel = 'root.lighting_sapb1'
        WHERE channel = 'root.sapb1.lighting'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE queue_job_channel
        SET name = 'lighting_sapb1', complete_name = 'root.lighting_sapb1'
        WHERE name = 'lighting' and complete_name = 'root.sapb1.lighting'
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        SELECT id
        from queue_job_channel
        WHERE complete_name = 'root.lighting_sapb1'
        """,
    )
    channel_ids = env.cr.fetchall()
    if not channel_ids:
        raise openupgrade.do_raise(
            "Expected at least one channel with new complete_name 'root.lighting.sapb1'"
        )
    channel_id = channel_ids[0][0]
    openupgrade.add_xmlid(
        env.cr,
        "connector_lighting_sapb1",
        "channel_lighting_sapb1",
        "queue.job.channel",
        channel_id,
        noupdate=True,
    )
