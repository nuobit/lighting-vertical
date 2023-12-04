# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Lighting Reporting",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions S.L.",
    "license": "AGPL-3",
    "category": "Custom",
    "website": "https://github.com/NuoBiT/lighting-vertical",
    "external_dependencies": {
        "python": [
            "Pillow",
        ],
    },
    "depends": [
        "lighting",
        # "lighting_seo",
        # "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/datasheet_wizard_views.xml",
        "report/report.xml",
        "views/report_product.xml",
        "views/product_views.xml",
        "views/product_attachment_type_views.xml",
    ],
    "assets": {
        "web.report_assets_pdf": [
            "lighting_reporting/static/src/scss/styles.scss",
        ],
    },
    "installable": True,
}
