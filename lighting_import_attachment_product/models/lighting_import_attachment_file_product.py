# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LightingImportAttachmentFileProduct(models.Model):
    _name = "lighting.import.attachment.file.product"
    _description = "Lighting Import Attachment File Product"

    product_id = fields.Many2one(
        comodel_name="lighting.product",
        required=True,
    )
    file_id = fields.Many2one(
        comodel_name="lighting.import.attachment.file",
        required=True,
        ondelete="cascade",
    )
    file_datas_fname = fields.Char(string="Filename", required=True)

    @api.constrains("product_id")
    def _check_product_id(self):
        for rec in self:
            if rec.product_id and rec.file_id.file_product_ids.filtered(
                lambda r: r.product_id == rec.product_id and r.id != rec.id
            ):
                raise ValidationError(_("Product already exists"))

    def _import(self):
        for rec in self:
            # find existing attahcments
            attachment_ids = self.env["lighting.attachment"].search(
                [
                    ("product_id", "=", rec.product_id.id),
                ]
            )

            attach_d = attachment_ids.filtered(
                lambda x: x.checksum == rec.file_id.checksum
            )
            if len(attach_d) > 1:
                raise ValidationError(_("Duplicate checksum %s") % rec.file_id.checksum)
            if len(attach_d) == 1:
                attach_d = attach_d[0]
            values = {}
            if not attach_d:
                values["datas"] = rec.file_id.datas
                # search by filename to be able to overwrite the ones with the same name
                attach_d = attachment_ids.filtered(
                    lambda x: x.datas_fname == rec.file_datas_fname
                )
                if attach_d:
                    attach_sorted_d = attach_d.sorted(
                        key=lambda x: (
                            x.write_date or "1900-01-01 00:00:00",
                            x.id,
                        ),
                        reverse=True,
                    )
                    attach_d, attach_to_remove_ld = (
                        attach_sorted_d[0],
                        attach_sorted_d[1:],
                    )
                    if attach_to_remove_ld:
                        raise ValidationError(
                            _(
                                "The file %(file)s has more than one attachment with "
                                "the same name in the product with reference: %(ref)s"
                            )
                            % {
                                "file": rec.file_id.datas_fname,
                                "ref": rec.product_id.reference,
                            }
                        )
            if not attach_d:
                values.update(
                    {
                        "type_id": rec.file_id.attachment_type_id.id,
                        "datas_location": "file",
                        "datas_fname": rec.file_datas_fname,
                    }
                )
                op = (0, 0)
            else:
                new_values = {}
                if (
                    not attach_d.datas_fname
                    or attach_d.datas_fname != rec.file_datas_fname
                ):
                    new_values["datas_fname"] = rec.file_datas_fname
                if attach_d.datas_location != "file":
                    raise ValidationError(
                        _("Unexpected: Attachment location is not file")
                    )
                if attach_d.type_id != rec.file_id.attachment_type_id:
                    raise ValidationError(
                        _("Unexpected: Attachment type is not %s")
                        % rec.file_id.attachment_type_id.code
                    )
                op = (1, attach_d.id)
                if new_values:
                    values.update(new_values)
            ops = []
            if values:
                if op[0] == 0:
                    values["product_id"] = rec.product_id.id
                values["date"] = fields.Datetime.now()
                ops.append((*op, values))
            if ops:
                rec.product_id.attachment_ids = ops
