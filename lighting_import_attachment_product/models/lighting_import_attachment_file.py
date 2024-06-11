# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging
import re
import unicodedata

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class LightingImportAttachmentFile(models.Model):
    _inherit = "lighting.import.attachment.file"

    message_info = fields.Selection(
        selection_add=[
            ("family_not_found", "Family not found"),
            ("no_products_found", "No products found"),
            # ("multiple_family_matches", "Multiple family matches"),
            # ("family_name_mismatch", "Family name mismatch"),
            # ("product_ref_pattern_mismatch", "Product reference pattern mismatch"),
            ("attachment_struct_error", "Attachment structure error"),
        ]
    )
    file_product_ids = fields.One2many(
        comodel_name="lighting.import.attachment.file.product",
        inverse_name="file_id",
    )
    family_ids = fields.Many2many(
        comodel_name="lighting.product.family",
        relation="lighting_import_attachment_file_product_family_rel",
        column1="file_product_id",
        column2="family_id",
    )
    attachment_type_id = fields.Many2one(
        comodel_name="lighting.attachment.type",
        readonly=True,
        ondelete="restrict",
    )
    allow_multiple_files = fields.Boolean()
    is_import_file_policy_variable = fields.Boolean(
        compute="_compute_is_import_file_policy_variable",
    )

    @api.depends("attachment_type_id")
    def _compute_is_import_file_policy_variable(self):
        for rec in self:
            rec.is_import_file_policy_variable = (
                rec.attachment_type_id.is_import_file_policy_variable
            )

    def action_allow_multiple_files(self):
        for rec in self:
            rec.allow_multiple_files = not rec.allow_multiple_files

    @api.constrains("allow_multiple_files")
    def _check_allow_multiple_files(self):
        for rec in self:
            if (
                rec.message_info
                and not rec.attachment_type_id.is_import_file_policy_variable
            ):
                raise ValidationError(
                    _(
                        "To change the allow multiple files policy, you must set the "
                        "import file policy variable in the attachment type."
                    )
                )
            if rec.import_attachment_id.state == "imported":
                raise ValidationError(
                    _("You can not change this field in imported attachments")
                )

    def slug(self, s):
        return (
            unicodedata.normalize("NFKD", s.replace(" ", ""))
            .encode("ASCII", "ignore")
            .decode("ASCII")
        )

    def check_unaccent(self):
        self.env.cr.execute(
            "select count(1) from pg_extension where extname = 'unaccent'"
        )
        count = self.env.cr.fetchone()[0]
        if count != 1:
            raise ValidationError(
                _(
                    "PostgreSQL 'unaccent' extension is not installed. It's necessary"
                    " in order for the County heuristic to work."
                )
            )

    # TODO: Review improve this method
    def parse_reference_structure(self, ref_struct):
        parse_error = None
        patterns = [
            (
                r"^(?P<fam_code>[^-]+)-(?P<params>[^-]+)-"
                r"(?P<finish1>[^-]{2})-(?P<finish2>[^-]{2})$",
                "%(fam_code)s-%(params)s-%(finish1)s-%(finish2)s",
            ),  # finish2
            (
                r"^(?P<fam_code>[^-]+)-(?P<params>[^-]+)-(?P<finish1>[^-]{2})",
                "%(fam_code)s-%(params)s-%(finish1)s",
            ),  # finish1
            (
                r"^(?P<fam_code>[^-]+)-(?P<params>[^-]+)",
                "%(fam_code)s-%(params)s",
            ),  # params,
            (r"^(?P<fam_code>[^-]+)", "%(fam_code)s"),  # family
        ]
        for pattern, check in patterns:
            match = re.match(pattern, ref_struct)
            if match:
                ref_parts = match.groupdict()
                formatted_ref = check % ref_parts
                if formatted_ref != ref_struct:
                    parse_error = "attachment_struct_error"
                exact_match = pattern[-1] == "$"
                break
        else:
            parse_error = "attachment_struct_error"
        ref_parts_search = {
            k: v.replace("x", "_") for k, v in ref_parts.items() if v is not None
        }
        ref_search = check % ref_parts_search
        ref_root_search = pattern % ref_parts_search
        if not exact_match:
            ref_search += "%"
            ref_root_search += ".*$"
        return {
            "check": check,
            "ref": ref_search,
            "ref_root": ref_root_search,
            "parse_error": parse_error,
        }

    def check_filepath_structure(self, datas_fname):
        self.ensure_one()
        res = {
            x: None
            for x in ["attach_type_name", "fam_name", "ref_struct", "info", "ext"]
        }
        m = re.match(
            r"^(?P<attach_type_name>[A-Z]{1,2})_(?P<fam_name>[^_]+)_"
            r"(?P<ref_struct>[^_]+)_(?P<info>[^.]+)\.(?P<ext>[^.]+)$",
            datas_fname,
        )
        if not m:
            m = re.match(
                r"^(?P<attach_type_name>[A-Z]{1,2})_(?P<fam_name>[^_]+)_"
                r"(?P<ref_struct>[^.]+)\.(?P<ext>[^.]+)$",
                datas_fname,
            )
            if not m:
                m = re.match(
                    r"^(?P<attach_type_name>[A-Z]{1,2})_(?P<fam_name>[^_]+)\."
                    "(?P<ext>[^.]+)$",
                    datas_fname,
                )
                if not m:
                    return None
        res.update(m.groupdict())
        return res

    def check(self):
        self.check_unaccent()
        for rec in self:
            values = rec.check_filepath_structure(rec.datas_fname)
            if not values:
                rec.message_info = "attachment_struct_error"
                continue
            if values["attach_type_name"]:
                attach_type = self.env["lighting.attachment.type"].search(
                    [("code", "=", values["attach_type_name"])]
                )
                rec.attachment_type_id = attach_type.id
                # assign allow_multiple_files value the first time
                if not rec.message_info and rec.attachment_type_id.allow_multiple_files:
                    rec.allow_multiple_files = True
            message_info = None

            # get families
            family = self.env["lighting.product.family"].search(
                [
                    ("name", "=ilike", values["fam_name"].replace("x", "_")),
                ],
                order="id",
            )
            if not family:
                # heuristic search
                fam_name_search_regexp = values["fam_name"].replace("x", ".")
                all_families_ld = self.env["lighting.product.family"].search(
                    [], order="id"
                )
                family = self.env["lighting.product.family"]
                for family_d in all_families_ld:
                    m = re.match(
                        r"^%s$" % rec.slug(fam_name_search_regexp),
                        rec.slug(family_d["name"]),
                        re.IGNORECASE,
                    )
                    if m:
                        family |= family_d
            if family:
                values["check"] = None
                values["ref_root"] = None
                rec.family_ids = family
                if values["ref_struct"]:
                    # find the parts of the reference
                    values.update(rec.parse_reference_structure(values["ref_struct"]))
                    if values["parse_error"]:
                        rec.message_info = values["parse_error"]
                        continue
                    domain = [("reference", "=ilike", values["ref"])]
                else:
                    domain = [("family_ids", "in", family.ids)]

                products = self.env["lighting.product"].search(domain)
                if not products:
                    message_info = "no_products_found"
                new_products = products - rec.file_product_ids.product_id
                data_products = []
                for product in new_products:
                    attach_fname = rec.prepare_attachment_data(product, family, values)
                    data_products.append(
                        {
                            "file_id": rec.id,
                            "product_id": product.id,
                            "file_datas_fname": attach_fname,
                        }
                    )
                if data_products:
                    rec.file_product_ids = [(0, 0, data) for data in data_products]
            else:
                message_info = "family_not_found"
            rec.message_info = "checked" if not message_info else message_info

    # TODO: Review add errors to the message_info instead of raising them
    def prepare_attachment_data(self, product, family, values):
        # search if the families are coherent
        family_id = set(product.family_ids) & set(family)
        if len(family_id) > 1:
            raise ValidationError(
                _("More than one family match in product %s") % product.name
            )
        if not family_id:
            raise ValidationError(
                _(
                    "Family name on file %(filename)s does not match any family"
                    " on product %(product)s with families: %(families)s"
                )
                % {
                    "filename": self.datas_fname,
                    "product": product.name,
                    "families": ", ".join(product.family_ids.mapped("name")),
                }
            )
        family_id = family_id.pop()
        family = product.family_ids.filtered(lambda x: x.id == family_id.id)
        odoo_fam_name_slug = self.slug(family.name)

        # build attachment name
        attach_filename_l = [values["attach_type_name"], odoo_fam_name_slug]
        if values["ref_struct"]:
            m = re.match(values["ref_root"], product.reference)
            if not m:
                raise ValidationError(
                    _(
                        "Product reference %(ref)s does not match"
                        " the pattern %(pattern)s"
                    )
                    % {
                        "ref": product.reference,
                        "pattern": values["ref_root"],
                    }
                )
            reference_root = values["check"] % m.groupdict()
            attach_filename_l.append(reference_root)
        if values["info"] is not None:
            attach_filename_l.append(values["info"])
        attach_filename = "_".join(attach_filename_l) + "." + values["ext"]
        return attach_filename

    def import_attachments(self):
        for rec in self:
            rec.file_product_ids._import()
            rec.message_info = "imported"

    # TODO: Review put this method in xml
    def action_show_details(self):
        self.ensure_one()
        view = self.env.ref(
            "lighting_import_attachment_product.lighting_import_attachment_file_view_form"
        )
        return {
            "name": _("Product Details"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "lighting.import.attachment.file",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": self.id,
            "context": dict(
                self.env.context,
            ),
        }

    def unlink(self):
        for record in self:
            if record.message_info == "imported":
                raise ValidationError(_("You cannot delete imported records."))
        return super().unlink()

    @api.model_create_multi
    def create(self, vals_list):
        self = self.with_context(image_no_postprocess=True)
        return super(LightingImportAttachmentFile, self).create(vals_list)

    def write(self, vals):
        self = self.with_context(image_no_postprocess=True)
        return super(LightingImportAttachmentFile, self).write(vals)
