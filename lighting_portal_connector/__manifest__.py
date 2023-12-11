# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Lighting Portal Connector",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Lighting",
    "website": "https://github.com/NuoBiT/lighting-vertical",
    "external_dependencies": {"python": ["hdbcli"]},
    "depends": ["lighting", "lighting_portal"],
    "data": [
        "security/portal_connector_security.xml",
        "security/ir.model.access.csv",
        "views/portal_views.xml",
        "views/portal_connector_settings_views.xml",
        "wizard/portal_connector_sync_views.xml",
        "views/lighting_views.xml",
        "data/portal_connector_data.xml",
    ],
}
