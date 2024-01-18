# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import SUPERUSER_ID
from odoo.api import Environment


def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    tables = [
        ("sapb1_backend", "sapb1_lighting_backend", "sapb1_lighting_backend_id_seq"),
        (
            "sapb1_backend_catalog_map",
            "sapb1_lighting_backend_catalog_map",
            "sapb1_lighting_backend_catalog_map_id_seq",
        ),
        (
            "sapb1_backend_lang_map",
            "sapb1_lighting_backend_lang_map",
            "sapb1_lighting_backend_lang_map_id_seq",
        ),
        (
            "sapb1_backend_state_marketing_map",
            "sapb1_lighting_backend_state_marketing_map",
            "sapb1_lighting_backend_state_marketing_map_id_seq",
        ),
        (
            "sapb1_light_product",
            "sapb1_lighting_product",
            "sapb1_lighting_product_id_seq",
        ),
    ]

    models = [x[0].replace("_", ".") for x in tables]
    states = ["installed", "to upgrade", "to remove"]
    if env["ir.module.module"].search(
        [("name", "=", "connector_sapb1")]
    ).state in states and env["ir.model"].search_count(
        [("model", "in", models)]
    ) == len(
        models
    ):
        for src, tgt, seq in tables:
            select_sql = "SELECT * FROM %s" % src
            cr.execute(select_sql)
            fields = [desc[0] for desc in cr.description]

            insert_sql = "insert into %s(%s) select * from %s" % (
                tgt,
                ", ".join(fields),
                src,
            )
            cr.execute(insert_sql)

            sequence_sql = "select setval('%s', (select max(id) from %s))" % (seq, tgt)
            cr.execute(sequence_sql)
