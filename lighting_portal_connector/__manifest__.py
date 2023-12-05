# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Lighting Portal Connector",
    "description": "Lighting Portal Connector",
    "version": "11.0.0.5.0",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Custom",
    "website": "https://github.com/NuoBiT/lighting-vertical",
    "depends": ["lighting", "lighting_portal"],
    "data": [
        "security/portal_connector_security.xml",
        "security/ir.model.access.csv",
        "views/portal_views.xml",
        "views/portal_connector_views.xml",
        "wizard/portal_connector_sync_views.xml",
        "data/portal_connector_data.xml",
    ],
    "installable": True,
}
