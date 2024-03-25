# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting Reporting",
    'description': """* Product datasheet""",
    'version': '11.0.0.14.1',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'external_dependencies': {
        'python': [
            'PIL',
        ],
    },
    'depends': [
        'lighting',
        'lighting_seo',
        'queue_job',
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'wizard/datasheet_wizard_views.xml',
        'report/report.xml',
        'views/report_product.xml',
        'views/product_views.xml',
        'views/product_attachment_views.xml',
        'views/product_attachment_type_views.xml',
    ],
    'installable': True,
}
