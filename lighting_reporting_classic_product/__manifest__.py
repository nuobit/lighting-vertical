# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Lighting Reporting Classic Product",
    "summary": "Product report for the classic template.",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Lighting",
    "website": "https://github.com/NuoBiT/lighting-vertical",
    "external_dependencies": {
        "python": [
            "Pillow",
        ],
    },
    "depends": [
        "lighting_reporting_product",
    ],
    "data": [
        "report/report.xml",
        "views/report_classic.xml",
    ],
    "assets": {
        "web.report_assets_pdf": [
            "lighting_reporting_classic_product/static/src/scss/styles.scss",
        ],
    },
    "post_init_hook": "post_init_hook",
}
