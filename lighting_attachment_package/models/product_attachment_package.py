# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import io
import zipfile
import base64

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


def pretty_size(value):
    conv = ['B', 'KB', 'MB', 'GB']
    i = 0
    while True:
        if value / 1024 < 1:
            if i >= len(conv):
                value_str = 'Inf'
            else:
                value_str = '%.1f %s' % (value, conv[i])
            break
        value /= 1024
        i += 1

    return value_str


class LightingAttachmentPackage(models.Model):
    _name = 'lighting.attachment.package'

    name = fields.Char(string='Description')

    catalog_ids = fields.Many2many(
        string="Catalogs",
        comodel_name='lighting.catalog',
        relation='lighting_attachment_package_catalog_rel',
        column1='package_id',
        column2='catalog_id',
    )

    datas = fields.Binary(string="Document", attachment=True)
    datas_fname = fields.Char(string='Filename', required=True)

    file_size_human = fields.Char(
        string="Size",
        compute="_compute_file_size_human", readonly=True)

    def _compute_file_size_human(self):
        for rec in self:
            if rec.attachment_id.file_size:
                rec.file_size_human = pretty_size(rec.attachment_id.file_size)

    attachment_id = fields.Many2one(comodel_name='ir.attachment',
                                    compute='_compute_ir_attachment', readonly=True)

    @api.depends('datas')
    def _compute_ir_attachment(self):
        for rec in self:
            attachment_obj = rec.env['ir.attachment'] \
                .search([('res_field', '=', 'datas'),
                         ('res_id', '=', rec.id),
                         ('res_model', '=', rec._name)]) \
                .sorted('id', reverse=True)
            if attachment_obj:
                rec.attachment_id = attachment_obj[0]
            else:
                rec.attachment_id = False

    lang_id = fields.Many2one(
        string="Language",
        comodel_name='lighting.language',
        ondelete='restrict',
    )

    last_update = fields.Datetime(
        string="Last update",
        readonly=True,
    )

    type_id = fields.Many2one(
        string='Type',
        required=True,
        comodel_name='lighting.attachment.type',
        ondelete='restrict'
    )

    def generate_zip_file(self):
        domain = [
            ('type_id', '=', self.type_id.id),
            ('product_id.website_published', '=', True),
        ]
        if self.catalog_ids:
            domain.append(('product_id.catalog_ids', 'in', self.catalog_ids.ids))
        if self.lang_id:
            domain.append(('lang_id.code', '=', self.lang_id.code))
        attachs = self.env['lighting.attachment'].search(domain) \
            .sorted(lambda x: (x.product_id.family_ids.mapped('name')[:1],
                               x.product_id.reference, x.datas_fname))
        in_memory = io.BytesIO()
        zf = zipfile.ZipFile(in_memory, mode="w",
                             compression=zipfile.ZIP_DEFLATED, compresslevel=9)
        for a in attachs:
            zf.write(self.env['ir.attachment']._full_path(
                a.attachment_id.store_fname), arcname=a.datas_fname)
        zf.close()
        in_memory.seek(0)
        file_bin = in_memory.read()
        in_memory.close()
        return file_bin

    def generate_pdf_file(self):
        if not self.lang_id:
            raise UserError(_("Language not selected in %s") % self.datas_fname)
        domain = [
            ('website_published', '=', True),
        ]
        if self.catalog_ids:
            domain.append(('catalog_ids', 'in', self.catalog_ids.ids))
        products = self.env['lighting.product'].search(domain).sorted(
            lambda x: (x.family_ids.mapped('name')[:1], x.reference))
        return self.env.ref('lighting_reporting.action_report_product'). \
            with_context(lang=self.lang_id.code).render_qweb_pdf(products.ids)[0]

    def generate_file_button(self):
        self.last_update = fields.datetime.now()
        # TODO: use check field to mark technical spreadsheet
        if self.type_id.code == 'FT':
            file_bin = self.generate_pdf_file()
        else:
            file_bin = self.generate_zip_file()

        self.datas = base64.b64encode(file_bin)
