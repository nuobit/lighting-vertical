# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LightingBMEcatConfig(models.Model):
    _name = "lighting.bmecat.config"
    _description = "Lighting BMEcat Configuration"

    name = fields.Char()
    default = fields.Boolean()
    version = fields.Selection(
        selection=[
            ("etim_5_0", "BMEcat_ETIM_5.0"),
        ],
        required=True,
        default="etim_5_0",
    )
    generator_info = fields.Char(default="Odoo Lighting")
    chunk_size = fields.Integer(
        string="Chunk Size (MB)",
        default=1,
        required=True,
        help="Chunk size in MB used when reading files. A larger chunk size can "
        "improve performance for large files but may increase memory usage.",
    )
    cache_clear_limit = fields.Integer(
        default=10000,
        help="Number of records to clear cache.",
        required=True,
    )
    ecommerce_datasheet_download_url = fields.Char(
        required=True,
        help="URL to download datasheets from the e-commerce site. If '%(reference)s' "
        "is included, it will be replaced by the product's reference.",
    )
    ecommerce_catalog_url = fields.Char(
        required=True,
        help="URL to access the e-commerce catalog. If '%(reference)s' is included, "
        "it will be replaced by the product's reference.",
    )
    validate_xml = fields.Boolean(
        string="Validate XML",
        default=True,
        help="If enabled, the XML files will be validated against their respective XSD schema.",
    )
    state_marketing_filter = fields.Many2many(
        "ir.model.fields.selection",
        string="Marketing Status Filter",
        domain=[
            ("field_id.model", "=", "lighting.product"),
            ("field_id.name", "=", "state_marketing"),
        ],
        help="Select marketing states to filter products during export.",
    )
    packing_unit_ids = fields.One2many(
        comodel_name="lighting.bmecat.packing.unit.mapping",
        inverse_name="config_id",
    )
    mime_code_ids = fields.One2many(
        comodel_name="lighting.bmecat.mime.code.mapping",
        inverse_name="config_id",
    )
    logistic_details_ids = fields.One2many(
        comodel_name="lighting.bmecat.logistic.details",
        inverse_name="config_id",
    )

    def get_chunk_size_bytes(self):
        return self.chunk_size * 1024 * 1024

    @api.constrains("default")
    def _check_default(self):
        for rec in self:
            if rec.default:
                if self.search([("default", "=", True), ("id", "!=", rec.id)]):
                    raise ValidationError(
                        _("There can only be one default BMEcat configuration.")
                    )
