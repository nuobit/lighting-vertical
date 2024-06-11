# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Lighting Import Attachment Product",
    "summary": "Management and processing of the import of product attachments",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Lighting",
    "website": "https://github.com/NuoBiT/lighting-vertical",
    "depends": ["lighting_import_attachment"],
    "data": [
        "security/ir.model.access.csv",
        "views/lighting_import_attachment_product_views.xml",
        "views/lighting_import_attachment_file_views.xml",
        "views/lighting_import_attachment_file_product_views.xml",
        "views/product_attachment_type_views.xml",
    ],
}
