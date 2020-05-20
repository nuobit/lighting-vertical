# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting Reporting",
    'description': """* Product data sheet""",
    'version': '12.0.1.0.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': ['lighting'],
    'data': [
        'report/product_report.xml',
        'report/product_report_templates.xml',
        'views/product_views.xml',
        ],
    'installable': True,
}
