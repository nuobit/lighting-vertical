# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Connector FTP attachment",
    'description': "Connector to upload attachments to FTP",
    'version': '11.0.1.0.2',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Connector',
    'website': 'https://github.com/nuobit',
    'depends': [
        'lighting_attachment_package',
        'connector',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/backend_views.xml',
        'views/menus.xml',
        'views/product_attachment_views.xml',
    ],
    'installable': True,
}
