# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LightingProductAddAttachment(models.TransientModel):
    """
    This wizard will allow to attach multiple files at once
    """

    _name = "lighting.product.addattachment"
    _description = "Attach multiple files at once"

    name = fields.Char(string="Description", translate=True)
    type_id = fields.Many2one(
        comodel_name="lighting.attachment.type",
        ondelete="cascade",
        required=True,
        string="Type",
    )

    datas_location = fields.Selection(
        string="Location",
        selection=[("file", "File"), ("url", "Url")],
        default="file",
        required=True,
    )

    datas_url = fields.Char(string="Url")

    datas = fields.Binary(string="Document", attachment=True)
    datas_fname = fields.Char(string="Filename")

    lang_id = fields.Many2one(
        comodel_name="lighting.language", ondelete="cascade", string="Language"
    )

    overwrite = fields.Boolean(string="Overwrite", default=False)

    result = fields.Char(string="Result", readonly=True)

    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("error", "Error"),
            ("done", "Done"),
        ],
        string="Status",
        default="pending",
        readonly=True,
        required=True,
        copy=False,
        track_visibility="onchange",
    )

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = "%s (%s)" % (record.datas_fname, record.type_id.display_name)
            vals.append((record.id, name))

        return vals

    @api.constrains("datas_location", "datas_url", "datas", "datas_fname")
    def _check_location_data_coherence(self):
        for rec in self:
            if rec.datas_location == "file":
                if rec.datas_url:
                    raise ValidationError(
                        _(
                            "There's a Url defined and the location type is not 'Url'. "
                            "Please change the Location to 'Url' or clean the url data first"
                        )
                    )
            elif rec.datas_location == "url":
                if rec.datas or rec.datas_fname:
                    raise ValidationError(
                        _(
                            "There's a File defined and the location type is not 'File'. "
                            "Please change the Location to 'File' or clean the file data first"
                        )
                    )
            else:
                raise ValidationError(
                    _("Attachment with Location not supported '%s'")
                    % rec.datas_location
                )

    @api.multi
    def add_attachment(self):
        # get products
        context = dict(self._context or {})
        active_ids = context.get("active_ids", []) or []
        products = self.env["lighting.product"].browse(active_ids)

        # construct the values
        values = {
            "type_id": self.type_id.id,
            "datas_location": self.datas_location,
        }
        if self.name:
            values["name"] = self.name
        if self.lang_id:
            values["lang_id"] = self.lang_id.id

        if self.datas_location == "file":
            values.update(
                {
                    "datas": self.datas,
                    "datas_fname": self.datas_fname,
                }
            )
            reset_default_domain = [
                "|",
                ("res_field", "=", False),
                ("res_field", "!=", False),
            ]
            addattach = self.env["ir.attachment"].search(
                reset_default_domain
                + [
                    ("res_model", "=", "lighting.product.addattachment"),
                    ("res_id", "=", self.id),
                ]
            )
        elif self.datas_location == "url":
            values.update(
                {
                    "datas_url": self.datas_url,
                }
            )

        errors = {}
        for product in products:
            # check if attach already exists
            attach_grouped = {}
            for attach in product.attachment_ids.filtered(
                lambda x: x.datas_location == self.datas_location
                and x.type_id == self.type_id
            ):
                if attach.datas_location == "file":
                    # get product Odoo attach object
                    ir_attach = self.env["ir.attachment"].search(
                        reset_default_domain
                        + [
                            ("res_model", "=", "lighting.attachment"),
                            ("res_id", "=", attach.id),
                        ],
                        order="id",
                    )
                    if not ir_attach:
                        continue
                    ir_attach = ir_attach[0]
                    if ir_attach.checksum == addattach.checksum:
                        attach_grouped.setdefault("bydatas", []).append(attach)
                    else:
                        if attach.datas_fname.lower() == self.datas_fname.lower():
                            attach_grouped.setdefault("byfname", []).append(attach)
                elif attach.datas_location == "url":
                    if ir_attach.datas_url.lower() == addattach.datas_url.lower():
                        attach_grouped.setdefault("bydatas", []).append(attach)

            if attach_grouped:
                for gtype, attachs in attach_grouped.items():
                    if gtype == "bydatas":
                        errors.setdefault(product.id, {"product": product})[
                            "same_checksum_match"
                        ] = attachs
                    elif gtype == "byfname":
                        if len(attachs) > 1:
                            errors.setdefault(product.id, {"product": product})[
                                "more_than_one_fname_match"
                            ] = attachs
                        elif len(attachs) == 1:
                            if self.overwrite:
                                product.attachment_ids = [(1, attachs[0].id, values)]
                            else:
                                product.attachment_ids = [(0, False, values)]
            else:
                product.attachment_ids = [(0, False, values)]

        msg = []
        for data in errors.values():
            msg0 = []
            if "same_checksum_match" in data:
                msg0.append(
                    _(
                        "Already exists other attachment with exactly the same content: %s"
                    )
                    % ", ".join({x.display_name for x in data["same_checksum_match"]})
                )
            if "more_than_one_fname_match" in data:
                msg0.append(
                    _("More than one attachment found with the same name: %s")
                    % ", ".join(
                        {x.display_name for x in data["more_than_one_fname_match"]}
                    )
                )
            msg.append("> %s: %s" % (data["product"].reference, ", ".join(msg0)))

        if msg != []:
            msg = [_("Completed with ERRORS:")] + msg
            self.result = "\n".join(msg)
            self.state = "error"
        else:
            self.result = _("Completed without errors")
            self.state = "done"

        return {"type": "ir.actions.do_nothing"}
