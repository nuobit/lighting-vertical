# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Connector FTP attachment",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/NuoBiT/lighting-vertical",
    "depends": [
        "lighting_attachment_package",
        "connector",
    ],
    "data": [
        "data/queue_data.xml",
        "data/queue_job_function_data.xml",
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/backend_views.xml",
        "views/menus.xml",
        "views/product_attachment_views.xml",
    ],
}
