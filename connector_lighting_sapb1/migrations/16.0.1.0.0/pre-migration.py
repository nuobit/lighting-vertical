# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_model_renames = [
    ("sapb1.lighting.backend", "lighting.sapb1.backend"),
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
        SET channel = 'root.lighting.sapb1'
        WHERE channel = 'root.sapb1.lighting'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE queue_job_function
        SET channel = 'root.lighting.sapb1'
        WHERE channel = 'root.sapb1.lighting'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        Select *
        from queue_job_channel
        WHERE complete_name = 'root.sapb1.lighting'
        """,
    )
    channel_id = env.cr.fetchone()

    if channel_id:
        channel_id = channel_id[0]
        openupgrade.logged_query(
            env.cr,
            """
            DELETE
            from queue_job_function
            WHERE channel_id = %(channel_id)s;
             DELETE
            from queue_job_channel
            WHERE id = %(channel_id)s
            """,
            args=dict(
                channel_id=channel_id,
            ),
        )
