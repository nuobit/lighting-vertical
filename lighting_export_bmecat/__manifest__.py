# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Lighting Export BMEcat",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Lighting",
    "website": "https://github.com/NuoBiT/lighting-vertical",
    "depends": ["lighting", "report_xml", "queue_job", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/lighting_bmecat_rule.xml",
        "data/mime_codes_data.xml",
        "data/packing_units_data.xml",
        "views/queue_job_views.xml",
        "views/lighting_export_bmecat_views.xml",
        "views/lighting_bmecat_config_views.xml",
        "views/product_catalog_views.xml",
        "views/report_bmecat.xml",
    ],
    "external_dependencies": {
        "python": ["pycountry"],
    },
}
