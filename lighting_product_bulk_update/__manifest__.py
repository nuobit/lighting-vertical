# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Lighting Product Bulk Update",
    "summary": "This module allows to bulk update products through a wizard",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Lighting",
    "website": "https://github.com/NuoBiT/lighting-vertical",
    "depends": ["lighting", "lighting_seo"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/product_bulk_update_views.xml",
        "views/lighting_views.xml",
    ],
}
