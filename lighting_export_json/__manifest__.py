# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Lighting JSON Export",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Lighting",
    "website": "https://github.com/NuoBiT/lighting-vertical",
    "depends": ["lighting_seo", "lighting_export", "report_json", "queue_job"],
    "data": [
        "data/export_template_data.xml",
        "report/export_product_json_reports.xml",
        "views/export_template_views.xml",
        "views/product_family_views.xml",
        "views/product_special_spectrum_views.xml",
        "wizard/export_views.xml",
    ],
}
