# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Lighting SEO/SEM",
    "description": "Add SEO/SEM capabilities to Lighting vertical",
    "version": "11.0.0.8.4",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Custom",
    "website": "https://github.com/NuoBiT/lighting-vertical",
    "depends": ["lighting"],
    "data": [
        "security/ir.model.access.csv",
        "security/lighting_seo_security.xml",
        "views/seo_keyword_views.xml",
        "views/product_views.xml",
    ],
    "installable": True,
}
