# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from openupgradelib import openupgrade

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

SPECIAL_SPECTRUM_MAP = {
    "meat": "Meat",
    "fashion": "Fashion",
    "multifood": "Multi Food",
    "bread": "Bread",
    "fish": "Fish",
    "vegetable": "Vegetable",
    "blue": "Blue",
    "orange": "Orange",
    "green": "Green",
    "red": "Red",
    "purple": "Purple",
    "pink": "Pink",
    "sunlike": "Sunlike",
    "dtw": "DtW",
    "tw": "TW",
}


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    _logger.info("Migration of special_spectrum to special_spectrum_id.")

    env.cr.execute(
        """
        SELECT DISTINCT special_spectrum
        FROM lighting_product_source_line
        WHERE special_spectrum IS NOT NULL
    """
    )
    records = env.cr.fetchall()
    languages = env["res.lang"].search([("code", "!=", "en_US")])
    for (code,) in records:
        special_spectrum = (
            env["lighting.product.special.spectrum"]
            .with_context(lang="en_US")
            .create(
                {
                    "name": SPECIAL_SPECTRUM_MAP[code],
                }
            )
        )
        for lang in languages:
            translation = env["ir.translation"].search(
                [
                    ("src", "=", special_spectrum.name),
                    ("name", "=", "lighting.product.source.line,special_spectrum"),
                    ("lang", "=", lang.code),
                ]
            )
            if len(translation) > 1:
                raise ValidationError(
                    "There is more than one translation for special spectrum %s"
                    % special_spectrum.name
                )
            if translation:
                special_spectrum.with_context(lang=lang.code).name = translation.value
        env.cr.execute(
            """
            UPDATE lighting_product_source_line
            SET special_spectrum_id = %s
            WHERE special_spectrum = %s AND special_spectrum IS NOT NULL
        """,
            (special_spectrum.id, code),
        )
