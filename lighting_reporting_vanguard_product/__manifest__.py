# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Lighting Reporting Vanguard Product",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Lighting",
    "website": "https://github.com/NuoBiT/lighting-vertical",
    "depends": [
        "lighting_reporting_product",
    ],
    "data": [
        "report/report.xml",
        "views/report_vanguard.xml",
    ],
    "assets": {
        "web.report_assets_pdf": [
            "lighting_reporting_vanguard_product/static/src/scss/styles.scss",
        ],
    },
    "post_init_hook": "post_init_hook",
}
