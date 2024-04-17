# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Lighting Attachment Import SMB",
    "summary": "Management of the SMB protocol for the import of attachments.",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Lighting",
    "website": "https://github.com/NuoBiT/lighting-vertical",
    "external_dependencies": {
        "python": [
            "pysmb",
        ],
    },
    "depends": ["lighting_import_attachment"],
    "data": [
        "security/ir.model.access.csv",
        "views/lighting_import_attachment_views.xml",
        "views/lighting_import_backend_views.xml",
        "views/lighting_import_attachment_smb_views.xml",
    ],
}
