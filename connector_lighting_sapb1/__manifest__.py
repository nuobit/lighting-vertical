# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Connector Lighting SAP B1",
    'description': "SAP Business One connector",
    'version': '11.0.0.1.1',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Connector',
    'website': 'https://github.com/nuobit',
    'external_dependencies': {
        'python': [
            'paramiko',
            'hdbcli',
            'requests',
        ],
    },
    'depends': [
        'connector',
        'lighting',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/connector_sapb1.xml',
        'data/ir_cron.xml',
        'views/sapb1_backend_view.xml',
        'views/lighting_product_view.xml',
        'views/connector_sapb1_menu.xml',
    ],
    'installable': True,
    'post_init_hook': 'post_init_hook',
}
