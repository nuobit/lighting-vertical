# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting Attachment Package",
    'description': "Generate attachment packages",
    'version': '11.0.1.0.2',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': [
        'lighting',
        'lighting_seo',
        'lighting_reporting',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_attachment_views.xml',
    ],
    'installable': True,
}
