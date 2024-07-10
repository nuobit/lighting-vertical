# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "(DEPRECATED) Lighting Reporting SEO",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Lighting",
    "website": "https://github.com/NuoBiT/lighting-vertical",
    "depends": [
        "lighting_reporting",
        "lighting_seo",
    ],
    "data": [
        "views/report_product.xml",
    ],
    "assets": {
        "web.report_assets_pdf": [
            "lighting_reporting_seo/static/src/scss/styles.scss",
        ],
    },
    "auto_install": True,
}
