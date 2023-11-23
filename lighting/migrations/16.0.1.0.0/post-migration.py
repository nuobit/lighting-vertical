# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade


def update_catalog_image(env):
    attachments = env["ir.attachment"].search(
        [
            ("res_model", "=", "lighting.catalog"),
            ("res_field", "=", "image"),
            ("res_id", "!=", False),
        ]
    )
    for attachment in attachments:
        env["lighting.catalog"].browse(attachment.res_id).image_1920 = attachment.datas


@openupgrade.migrate()
def migrate(env, version):
    update_catalog_image(env)
    openupgrade.logged_query(
        env.cr,
        """
            delete
            from ir_attachment
            where res_model = 'lighting.catalog'
            and res_field in ('image_medium', 'image_small')
            """,
    )
