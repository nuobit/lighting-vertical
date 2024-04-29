# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Lighting Attachment Import Queue Job",
    "summary": "Management and processing of the import of product "
    "attachments with queues jobs",
    "version": "16.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Lighting",
    "website": "https://github.com/NuoBiT/lighting-vertical",
    "depends": ["lighting_import_attachment_product", "queue_job"],
    "data": [
        "data/lighting_import_attachment_product_queue_job.xml",
        "views/queue_job_views.xml",
        "views/lighting_import_attachment_views.xml",
        "views/lighting_import_attachment_file_views.xml",
    ],
}
