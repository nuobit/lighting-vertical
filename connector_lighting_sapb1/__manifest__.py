# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Connector Lighting SAP B1",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/NuoBiT/lighting-vertical",
    "external_dependencies": {
        "python": [
            "paramiko",
            "hdbcli",
            "requests",
        ],
    },
    "depends": [
        "connector_extension",
        "lighting",
    ],
    "data": [
        "data/queue_data.xml",
        "data/queue_job_function_data.xml",
        "security/ir.model.access.csv",
        "security/connector_sapb1.xml",
        "data/ir_cron.xml",
        "views/lighting_sapb1_backend_view.xml",
        "views/lighting_product_view.xml",
        "views/connector_sapb1_menu.xml",
    ],
}
