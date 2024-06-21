# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Lighting Reporting Product",
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
        "lighting",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/lighting_reporting_product_wizard_views.xml",
        "views/res_config_settings_views.xml",
        "views/lighting_product_views.xml",
        "views/lighting_attachment_type_views.xml",
    ],
    "assets": {
        "web.report_assets_pdf": [
            "lighting_reporting_product/static/src/scss/styles.scss",
        ],
    },
}
