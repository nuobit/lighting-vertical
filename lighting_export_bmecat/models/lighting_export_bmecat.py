# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import gzip
import hashlib
import itertools
import os
import shutil
import subprocess

from pycountry import languages

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


class LightingExportBMEcat(models.Model):
    _name = "lighting.export.bmecat"
    _description = "Lighting Export BMEcat"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "valid_start_date desc"

    name = fields.Char(required=True)
    bmecat_config_id = fields.Many2one(
        comodel_name="lighting.bmecat.config",
        required=True,
        tracking=True,
        default=lambda self: self.env["lighting.bmecat.config"]
        .search([("default", "=", True)])
        .id,
    )
    catalog_id = fields.Many2one(
        comodel_name="lighting.catalog", required=True, tracking=True
    )
    create_job = fields.Boolean()
    state = fields.Selection(
        selection=[
            ("draft", _("Draft")),
            ("generated", _("Generated")),
            ("validated", _("Validated")),
            ("published", _("Published")),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    attachment_id = fields.Many2one(
        comodel_name="ir.attachment", copy=False, tracking=True
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
        readonly=True,
    )
    valid_start_date = fields.Date(
        string="Publication Date", required=True, tracking=True
    )
    language_id = fields.Many2one(comodel_name="res.lang", required=True, tracking=True)
    bmecat_jobs_ids = fields.Many2many(
        comodel_name="queue.job",
        relation="lighting_export_bmecat_queue_job_rel",
        column1="bmecat_id",
        column2="job_id",
        string="Queue Job",
        copy=False,
    )
    lang_iso392_2 = fields.Char(compute="_compute_lang_iso392_2")

    def _compute_lang_iso392_2(self):
        for rec in self:
            if rec.language_id:
                rec.lang_iso392_2 = languages.get(
                    alpha_2=rec.language_id.iso_code
                ).alpha_3
            else:
                rec.lang_iso392_2 = False

    catalog_version = fields.Char(
        compute="_compute_catalog_version", store=True, readonly=False, tracking=True
    )

    @api.depends("valid_start_date")
    def _compute_catalog_version(self):
        for rec in self:
            if rec.valid_start_date:
                rec.catalog_version = "{:03d}.000".format(
                    rec.valid_start_date.year % 1000
                )
            else:
                rec.catalog_version = False

    @api.constrains("catalog_version")
    def _check_catalog_version(self):
        for rec in self:
            if len(rec.catalog_version) != 7:
                raise ValidationError(
                    _(
                        "The catalog version is not correct. It "
                        "should be in the format 'XXX.XXX'"
                    )
                )

    @api.constrains("state")
    def _check_state(self):
        for rec in self:
            if rec.state != "draft" and not rec.attachment_id:
                raise ValidationError(_("You must generate the BMEcat file first"))

    def get_mime_info(self, product):
        mime_info = {}
        index = 0
        for index, attach in enumerate(product.attachment_ids, start=1):
            mime_code = self.bmecat_config_id.mime_code_ids.filtered(
                lambda x: x.type_id == attach.type_id
            ).mime_code_id.code
            if mime_code:
                mime_info[index] = {
                    "mime_source": attach.url,
                    "mime_code": mime_code,
                    "mime_filename": attach.datas_fname[:250]
                    if attach.datas_fname
                    else False,
                    "mime_alt": "%s:%s" % (mime_code, attach.datas_fname),
                }
        mime_info[index + 1] = self.get_mime_md04(product)
        mime_info[index + 2] = self.get_mime_md22(product)
        return mime_info

    def _get_url_mime(self, product, url_func, code):
        return {
            "mime_source": url_func(product),
            "mime_code": code,
            "mime_filename": f"URL {code}",
            "mime_alt": f"URL {code}",
        }

    def get_mime_md04(self, product):
        return self._get_url_mime(product, self.get_product_web_url, "MD04")

    def get_mime_md22(self, product):
        return self._get_url_mime(product, self.get_datasheet_download_url, "MD22")

    def _format_url(self, url, product):
        if "%(reference)s" in url:
            return url % {"reference": product.reference}
        return url

    def get_product_web_url(self, product):
        base_url = self.bmecat_config_id.ecommerce_catalog_url
        return self._format_url(base_url, product)

    def get_datasheet_download_url(self, product):
        base_url = self.bmecat_config_id.ecommerce_datasheet_download_url
        return self._format_url(base_url, product)

    def get_packing_unit(self, product):
        return self.bmecat_config_id.packing_unit_ids.filtered(
            lambda x: x.uom_id == product.product_variant_id.uom_id
        ).packing_unit_id.code

    def get_logistic_values(self, product):
        if not product.dimension_ids:
            return {}
        logistic_details = self.bmecat_config_id.logistic_details_ids.sorted(
            key=lambda x: x.sequence
        )
        candidates_by_key = {}
        for ld in logistic_details:
            for dimension in product.dimension_ids:
                if dimension.value:
                    if dimension.type_id == ld.dimension_type_id:
                        if ld.uom_id != dimension.type_id.uom_id:
                            value = dimension.type_id.uom_id._compute_quantity(
                                dimension.value, ld.uom_id
                            )
                        else:
                            value = dimension.value
                        candidates_by_key.setdefault(ld.dimension, []).append(
                            [ld.sequence, ld.dimension_type_id.name, value]
                        )
        keys = list(candidates_by_key.keys())
        n = len(keys)
        best_assignment_dict = None
        best_cost = None
        best_num_keys = 0
        for r in range(n, 0, -1):
            for subset in itertools.combinations(keys, r):
                candidates_list = [candidates_by_key[k] for k in subset]
                for assignment in itertools.product(*candidates_list):
                    texts = [item[1] for item in assignment]
                    if len(set(texts)) == len(texts):
                        cost = sum(item[0] for item in assignment)
                        if (
                            best_assignment_dict is None
                            or r > best_num_keys
                            or (r == best_num_keys and cost < best_cost)
                        ):
                            best_assignment_dict = {
                                k: candidate[2]
                                for k, candidate in zip(subset, assignment)
                            }
                            best_cost = cost
                            best_num_keys = r
            if best_assignment_dict is not None:
                break
        return best_assignment_dict

    def validate_xml_with_xsd(self, xml_file_path):
        if self.bmecat_config_id.version == "etim_5_0":
            schema_path = get_module_resource(
                "lighting_export_bmecat",
                "data",
                "BMEcat_ETIM_5.0",
                "bmecat_etim_501.xsd",
            )
        else:
            raise ValidationError(_("The BMECat version is not supported."))
        # TODO REVIEW: Add installation of xmlstarlet in the pre_init_hook
        if shutil.which("xmlstarlet") is None:
            try:
                subprocess.run(
                    ["sudo", "apt", "install", "-y", "xmlstarlet"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            except subprocess.CalledProcessError as e:
                raise ValidationError(
                    _("Failed to install xmlstarlet: %s") % e.stderr
                ) from e
        result = subprocess.run(
            ["xmlstarlet", "val", "--err", "--xsd", schema_path, xml_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            raise ValidationError(_("The XML is not valid: %s") % result.stderr)

    def _check_bmecat_file_values(self, products):
        self.ensure_one()
        if not self.catalog_id.code:
            raise ValidationError(_("The catalog must have a code."))
        if not self.company_id.email:
            raise ValidationError(_("The company must have an email."))
        products_without_ref = products.filtered(lambda x: not x.reference)
        if products_without_ref:
            raise ValidationError(
                _("The following products do not have a reference: %s")
                % ", ".join(products_without_ref.mapped("name"))
            )
        products_without_desc_short = products.filtered(lambda x: not x.description)
        if products_without_desc_short:
            raise ValidationError(
                _("The following products do not have a description: %s")
                % ", ".join(products_without_desc_short.mapped("reference"))
            )
        products_without_packing_unit = products.filtered(
            lambda product: not self.bmecat_config_id.packing_unit_ids.filtered(
                lambda x: x.uom_id == product.product_variant_id.uom_id
            )
        )
        if products_without_packing_unit:
            raise ValidationError(
                _(
                    "The following products have no packing unit associated with "
                    "their measurement unit in the BMECat configuration: %s"
                )
                % ", ".join(products_without_packing_unit.mapped("reference"))
            )
        products_without_taxes = products.filtered(
            lambda x: not x.product_variant_id.taxes_id
        )
        if products_without_taxes:
            raise ValidationError(
                _("The following products do not have taxes: %s")
                % ", ".join(products_without_taxes.mapped("reference"))
            )
        products_without_dimensions = {}
        dimension_without_uom = {}
        for product in products:
            for dimension in product.dimension_ids:
                if dimension.value:
                    if (
                        dimension.type_id
                        not in self.bmecat_config_id.logistic_details_ids.dimension_type_id
                    ):
                        products_without_dimensions.setdefault(product, []).append(
                            dimension.type_id.name
                        )
                    if (
                        not dimension.type_id.uom_id
                        and dimension.type_id.name not in dimension_without_uom
                    ):
                        dimension_without_uom.setdefault(dimension.type_id.name)
        if products_without_dimensions:
            raise ValidationError(
                _(
                    "The following products have dimensions that are not "
                    "configured in the BMECat configuration:\n%s"
                )
                % "\n".join(
                    [
                        "%s (%s)" % (product.reference, ", ".join(dimensions))
                        for product, dimensions in products_without_dimensions.items()
                    ]
                )
            )
        if dimension_without_uom:
            raise ValidationError(
                _("The following dimensions do not have a UOM defined:\n%s")
                % "\n".join(dimension_without_uom)
            )

    def _compress_file(self, filename):
        temp_compressed_filename = filename + ".gz"
        chunk_size = self.bmecat_config_id.get_chunk_size_bytes()
        with open(filename, "rb") as f_in, gzip.open(
            temp_compressed_filename, "wb"
        ) as f_out:
            while True:
                chunk = f_in.read(chunk_size)
                if not chunk:
                    break
                f_out.write(chunk)
        os.remove(filename)
        os.rename(temp_compressed_filename, filename)

    def _compute_file_hash_and_size(self, filename):
        chunk_size = self.bmecat_config_id.get_chunk_size_bytes()
        sha1 = hashlib.sha1()
        with open(filename, "rb") as f:
            while chunk := f.read(chunk_size):
                sha1.update(chunk)
        content_hash = sha1.hexdigest()
        file_size = os.path.getsize(filename)
        return content_hash, file_size

    def _move_file_to_filestore(self, filename, filestore_path, content_hash):
        content_hash_dir = os.path.join(content_hash[:2], content_hash)
        final_path = os.path.join(filestore_path, content_hash_dir)
        if not os.path.exists(final_path):
            os.rename(filename, final_path)
        else:
            os.remove(filename)

    def _get_bmecat_filename(self):
        return (
            f"BMEcat_{self.catalog_id.name}_"
            f"{self.valid_start_date.strftime('%Y-%m')}_"
            f"{self.language_id.code}"
        )

    def _create_attachment(self, content_hash, file_size):
        attachment_vals = {
            "name": self._get_bmecat_filename() + ".zip",
            "res_model": "lighting.export.bmecat",
            "res_id": self.id,
            "type": "binary",
            "mimetype": "application/xml",
        }
        attachment = self.env["ir.attachment"].create(attachment_vals)
        self.env.cr.execute(
            "UPDATE ir_attachment SET store_fname=%s, file_size=%s, checksum=%s WHERE id=%s",
            (
                os.path.join(content_hash[:2], content_hash),
                file_size,
                content_hash,
                attachment.id,
            ),
        )
        return attachment

    def _write_bmecat_xml(self, file, products):
        file.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(
            b"<BMECAT\n"
            b'  xmlns="https://www.etim-international.com/bmecat/50"\n'
            b'  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
            b'  xsi:schemaLocation="https://www.etim-international.com/bmecat/50 '
            b'https://www.etim-international.com/bmecat_etim_50.xsd"\n'
            b'  version="2005"\n'
            b">\n"
        )
        file.write(
            self.env.ref("lighting_export_bmecat.action_report_bmecat_header")._render(
                "lighting_export_bmecat.action_report_bmecat_header",
                self.ids,
                data={"bmecat": self},
            )[0]
        )
        file.write(b"<T_NEW_CATALOG>\n")
        for counter, product in enumerate(products, start=1):
            file.write(
                self.env.ref(
                    "lighting_export_bmecat.action_report_bmecat_product"
                )._render(
                    "lighting_export_bmecat.action_report_bmecat_product",
                    self.ids,
                    data={"bmecat": self, "product": product},
                )[
                    0
                ]
            )
            if counter % self.bmecat_config_id.cache_clear_limit == 0:
                self.env.cache.clear()
        self.env.cache.clear()
        file.write(b"</T_NEW_CATALOG>\n")
        file.write(b"</BMECAT>\n")

    def send_bmecat_notification(self, attachment):
        self.message_post(attachment_ids=[attachment.id])
        if self.create_job:
            self = self.with_context(mail_notify_author=True)
        self.message_post(
            body=_(
                "The BMEcat catalog of %(catalog_name)s has been successfully generated."
            )
            % {"catalog_name": self.catalog_id.name},
            subtype_xmlid="mail.mt_comment",
            partner_ids=[self.env.user.partner_id.id],
        )

    def _generate_bmecat_file(self):
        self.ensure_one()
        products = self.env["lighting.product"].search(
            [
                ("catalog_ids", "=", self.catalog_id.id),
                (
                    "state_marketing",
                    "in",
                    self.bmecat_config_id.state_marketing_filter.mapped("value"),
                ),
                ("state", "=", "published"),  # TODO REVIEW: Reconsider logic
            ]
        )
        self._check_bmecat_file_values(products)
        filestore_path = self.env["ir.attachment"]._filestore()
        temp_filename = os.path.join(
            filestore_path, self._get_bmecat_filename() + ".xml"
        )
        with open(temp_filename, "w+b") as tmp_file:
            self._write_bmecat_xml(tmp_file, products)
        if self.bmecat_config_id.validate_xml:
            self.validate_xml_with_xsd(temp_filename)
        self._compress_file(temp_filename)
        content_hash, file_size = self._compute_file_hash_and_size(temp_filename)
        self._move_file_to_filestore(temp_filename, filestore_path, content_hash)
        attachment = self._create_attachment(content_hash, file_size)
        self.write(
            {
                "attachment_id": attachment.id,
                "state": "validated"
                if self.bmecat_config_id.validate_xml
                else "generated",
            }
        )
        self.with_context(lang=self.env.user.lang).send_bmecat_notification(attachment)

    def generate_bmecat_file(self):
        self.ensure_one()
        self = self.with_context(lang=self.language_id.code)
        if not self.create_job:
            return self._generate_bmecat_file()
        new_delay = self.with_delay()._generate_bmecat_file()
        job = self.env["queue.job"].search([("uuid", "=", new_delay.uuid)], limit=1)
        self.bmecat_jobs_ids |= job

    def action_download_bmecat_file(self):
        self.ensure_one()
        if not self.attachment_id:
            raise ValidationError(_("No BMECat file has been generated yet."))
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % self.attachment_id.id,
            "target": "self",
        }
