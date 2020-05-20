# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Lighting Project",
    'description': "Add lighting project portfolio",
    'version': '12.0.1.0.0',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': ['lighting'],
    'data': [
        'security/project_security.xml',
        'security/ir.model.access.csv',
        'views/project_menuitems.xml',
        'views/project_type_views.xml',
        'views/project_agent_views.xml',
        'views/project_attachment_views.xml',
        'views/project_views.xml',
        'views/product_views.xml',
        'report/project_reports.xml',
        'report/project_sheet_report_templates.xml',
        ],
    'installable': True,
}
