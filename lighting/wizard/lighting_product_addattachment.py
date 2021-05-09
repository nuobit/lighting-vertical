# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class LightingProductAddAttachment(models.TransientModel):
    """
    This wizard will allow to attach multiple files at once
    """

    _name = "lighting.product.addattachment"
    _description = "Attach multiple files at once"

    name = fields.Char(string='Description', translate=True)
    type_id = fields.Many2one(comodel_name='lighting.attachment.type', ondelete='cascade', required=True,
                              string='Type')

    datas_location = fields.Selection(
        string='Location',
        selection=[('file', 'File'), ('url', 'Url')],
        default='file',
        required=True
    )

    datas_url = fields.Char(string='Url')

    datas = fields.Binary(string="Document", attachment=True)
    datas_fname = fields.Char(string='Filename')

    lang_id = fields.Many2one(comodel_name='lighting.language', ondelete='cascade', string='Language')

    result = fields.Char(string='Result', readonly=True)

    state = fields.Selection([
        ('pending', 'Pending'),
        ('error', 'Error'),
        ('done', 'Done'),
    ], string='Status', default='pending', readonly=True, required=True, copy=False, track_visibility='onchange')

    @api.multi
    def name_get(self):
        vals = []
        for record in self:
            name = '%s (%s)' % (record.datas_fname, record.type_id.display_name)
            vals.append((record.id, name))

        return vals

    @api.constrains('datas_location', 'datas_url', 'datas', 'datas_fname')
    def _check_location_data_coherence(self):
        for rec in self:
            if rec.datas_location == 'file':
                if rec.datas_url:
                    raise ValidationError(
                        _("There's a Url defined and the location type is not 'Url'. "
                          "Please change the Location to 'Url' or clean the url data first"))
            elif rec.datas_location == 'url':
                if rec.datas or rec.datas_fname:
                    raise ValidationError(
                        _("There's a File defined and the location type is not 'File'. "
                          "Please change the Location to 'File' or clean the file data first"))
            else:
                raise ValidationError(_("Attachment with Location not supported '%s'") % rec.datas_location)

    @api.multi
    def add_attachment(self):
        # get products
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        products = self.env['lighting.product'].browse(active_ids)

        # construct the values
        values = {
            'name': self.name,
            'type_id': self.type_id.id,
            'lang_id': self.lang_id.id,
            'datas_location': self.datas_location,
        }
        if self.datas_location == 'file':
            values.update({
                'datas': self.datas,
                'datas_fname': self.datas_fname,
            })
            reset_default_domain = ['|', ('res_field', '=', False), ('res_field', '!=', False)]
            addattach = self.env['ir.attachment'].search(
                reset_default_domain +
                [('res_model', '=', 'lighting.product.addattachment'), ('res_id', '=', self.id)]
            )
        elif self.datas_location == 'url':
            values.update({
                'datas_url': self.datas_url,
            })

        errors = {}
        for product in products:
            # check if attach already exists
            for attach in product.attachment_ids.filtered(
                    lambda x: x.datas_location == self.datas_location):
                # check if already exists another attachment linked
                # with the same file or url
                duplicated = False
                if attach.datas_location == 'file':
                    # get product Odoo attach object
                    ir_attach = self.env['ir.attachment'].search(
                        reset_default_domain +
                        [('res_model', '=', 'lighting.attachment'), ('res_id', '=', attach.id)],
                        order='id'
                    )
                    if not ir_attach:
                        continue
                    ir_attach = ir_attach[0]
                    duplicated = ir_attach.checksum == addattach.checksum
                elif attach.datas_location == 'url':
                    duplicated = ir_attach.datas_url == addattach.datas_url

                if duplicated:
                    errors.setdefault(product.id, {'product': product})
                    if attach.type_id == self.type_id:
                        errors[product.id]['duplicated_same_type'] = True
                        break
                    else:
                        errors[product.id].setdefault('duplicated_diff_type', []) \
                            .append(attach.type_id)

            if product.id not in errors:
                product.attachment_ids = [(0, False, values)]

        msg = []
        for data in errors.values():
            msg0 = []
            if 'duplicated_same_type' in data:
                msg0.append(_('Already exists an attachment with the same type'))
            if 'duplicated_diff_type' in data:
                msg0.append(_('Already exists an attachment but with different types: %s') %
                            ', '.join({x.display_name for x in data['duplicated_diff_type']}))
            msg.append('> %s: %s' % (data['product'].reference, ', '.join(msg0)))

        if msg != []:
            msg = [_('Completed with ERRORS:')] + msg
            self.result = '\n'.join(msg)
            self.state = 'error'
        else:
            self.result = _('Completed without errors')
            self.state = 'done'

        return {
            'type': 'ir.actions.do_nothing'
        }
