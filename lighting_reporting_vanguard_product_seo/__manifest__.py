# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Lighting Reporting Vanguard Product SEO",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Lighting",
    "website": "https://github.com/NuoBiT/lighting-vertical",
    "depends": [
        "lighting_reporting_vanguard_product",
        "lighting_seo",
    ],
    "data": [
        "views/report_vanguard.xml",
    ],
    "assets": {
        "web.report_assets_pdf": [
            "lighting_reporting_vanguard_product_seo/static/src/scss/styles.scss",
        ],
    },
    "auto_install": True,
}
