# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.addons.queue_job.job import job

from PyPDF2 import PdfFileWriter, PdfFileReader
import base64
import io

import logging

_logger = logging.getLogger(__name__)


def chunks(li, n):
    if not li:
        return
    yield li[:n]
    yield from chunks(li[n:], n)


class LightingProduct(models.Model):
    _inherit = 'lighting.product'

    def product_datasheet_wizard(self):
        action = self.env.ref('lighting_reporting.product_datasheet_wizard_action').read()[0]
        return action

    @job(default_channel='root.lighting_datasheet_prepare')
    @api.model
    def update_product_datasheets(self, product_ids, lang_ids=None, delayed=False, force_update=False):
        """ Prepare background datasheet update """
        if lang_ids:
            langs = self.env['res.lang'].browse(lang_ids)
            llangs = self.env['lighting.language'].search([
                ('code', 'in', langs.mapped('code'))
            ])
        else:
            llangs = self.env['lighting.language'].search([])
        datasheet_types = self.env['lighting.attachment.type'].search([
            ('is_datasheet', '=', True)], order='sequence,id')

        for product_id in product_ids:
            for ds in datasheet_types:
                for llang in llangs:
                    attachments = self.env['lighting.attachment'].search([
                        ('product_id', '=', product_id),
                        ('type_id', '=', ds.id),
                        ('lang_id.code', '=', llang.code),
                    ])
                    if not attachments:
                        attachments |= self.env['lighting.attachment'].create({
                            'product_id': product_id,
                            'type_id': ds.id,
                            'lang_id': llang.id
                        })
                    for attach in attachments:
                        if not attach.manual:
                            if not attach.attachment_id or force_update:
                                if delayed:
                                    attach.with_delay().generate_datasheet(attach.id)
                                else:
                                    attach.generate_datasheet(attach.id)
                            else:
                                _logger.info("Datasheet from %i: %s (%s) already generated" % (
                                    product_id, ds.code, llang.code))

    def get_product_datasheet(self, lang_ids=None):
        self.update_product_datasheets(self.ids, lang_ids)
        if lang_ids:
            langs = self.env['res.lang'].browse(lang_ids)
            llangs = self.env['lighting.language'].search([
                ('code', 'in', langs.mapped('code'))
            ])
        attachments = self.mapped('attachment_ids') \
            .filtered(lambda x: x.type_id.is_datasheet and
                                (not lang_ids or x.lang_id.code in llangs.mapped('code'))) \
            .sorted(lambda x: (x.product_id.family_ids and x.product_id.family_ids[0] or '',
                               x.product_id.reference,
                               x.lang_id and x.lang_id.code or ''))
        streams = []
        for attach in attachments:
            content = base64.b64decode(attach.datas)
            streams.append(io.BytesIO(content))

        # Build the final pdf.
        writer = PdfFileWriter()
        for stream in streams:
            reader = PdfFileReader(stream)
            writer.appendPagesFromReader(reader)
        result_stream = io.BytesIO()
        streams.append(result_stream)
        writer.write(result_stream)
        result = result_stream.getvalue()

        # We have to close the streams after PdfFileWriter's call to write()
        for stream in streams:
            try:
                stream.close()
            except Exception:
                pass

        return result

    def get_sheet_sources(self):
        res = []
        for s in self.source_ids.sorted(lambda x: x.sequence):
            s_res = []
            s_type = s.get_source_type()
            if s_type:
                s_res.append(s_type[0])

            s_wattage = s.get_wattage()
            if s_wattage:
                s_res.append(s_wattage[0])

            s_flux = s.get_luminous_flux()
            if s_flux:
                s_res.append(s_flux[0])

            s_temp = s.get_color_temperature()
            if s_temp:
                s_res.append(s_temp[0])

            s_cri = s.get_cri()
            if s_cri:
                s_res.append(s_cri[0])

            s_spectrum = s.get_special_spectrum()
            if s_spectrum:
                s_res.append(s_spectrum[0].upper())

            if s_res:
                res.append(' '.join(s_res))

        return res

    def get_sheet_beams(self):
        res = []
        for b in self.beam_ids:
            b_res = []
            s_angle = b.get_beam_angle()
            if s_angle:
                b_res.append(s_angle[0])

            s_phm = b.get_beam_photometric_distribution()
            if s_phm:
                b_res.append(s_phm[0])

            if b_res:
                res.append(' - '.join(b_res))

        return res

    def get_is_lamp_included(self):
        line_ids = self.source_ids.mapped('line_ids')
        integrated_line_ids = line_ids.filtered(lambda x: x.is_integrated)
        lamp_included_line_ids = line_ids.filtered(lambda x: not x.is_integrated).mapped('is_lamp_included')
        if integrated_line_ids:
            return any(lamp_included_line_ids) or None
        else:
            return any(lamp_included_line_ids)

    @api.multi
    def filter_by_catalogued(self):
        return self.filtered(
            lambda x: x.state_marketing in ('N', 'C', 'ES')
        )

    def get_usb(self):
        res = []
        if self.usb_ports:
            res.append("(%g)" % self.usb_ports)

        res_usbv = []
        if self.usb_voltage:
            res_usbv.append("%gV" % self.usb_voltage)
        if self.usb_current:
            res_usbv.append("%gmA" % self.usb_current)

        if res_usbv:
            res.append(' '.join(res_usbv))

        if res:
            return ' x '.join(res)

        return None

    def get_operating_temperature_range(self):
        res = []
        if self.operating_temperature_min:
            res.append("%i" % self.operating_temperature_min)
        if self.operating_temperature_max:
            res.append("%i" % self.operating_temperature_max)

        if res:
            return '%s ºC' % ' - '.join(res)

        return None

    def get_datasheet_url(self):
        self.ensure_one()
        url = "{}/web/datasheet/{}/{}".format(
            self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            self.env.context.get('lang'),
            self.reference,
        )
        return url

    def get_attachments_by_type(self, atype, only_images=True):
        attachments = self.env['lighting.attachment']
        for rec in self:
            attachments |= rec.attachment_ids.filtered(
                lambda x: x.type_id.code == atype and
                          (not only_images or x.attachment_id.index_content == 'image')
            ).sorted(lambda x: (x.sequence, x.id))

        return attachments

    def get_complementary_fp_images(self, groupsof=None):
        # FP's current product
        attachments = self.get_attachments_by_type('FP')

        if not groupsof:
            groupsof = len(attachments)

        return list(chunks(attachments, groupsof))

    def get_complementary_fa_images(self, groupsof=None):
        # FA's current product
        attachments = self.get_attachments_by_type('FA')[2:]

        if not groupsof:
            groupsof = len(attachments)

        return list(chunks(attachments, groupsof))

    def get_groups_same_family(self, groupsof=None):
        groups = self.search([
            ('id', '!=', self.id),
            ('family_ids', 'in', self.family_ids.mapped('id')),
        ]).mapped('product_group_id') \
            .get_parent_group_by_type('PHOTO') \
            .filtered(lambda x: self not in x.flat_product_ids and
                                x.flat_product_ids.filter_by_catalogued() and
                                not all(x.flat_category_ids.mapped('root_id.is_accessory'))
                      ).sorted(lambda x: x.name)

        if not groupsof:
            groupsof = len(groups)

        return list(chunks(groups, groupsof))

    @api.multi
    def write(self, values):
        res = super().write(values)
        self.update_product_datasheets(self.ids, delayed=True, force_update=True)
        return res

    @api.model
    def create(self, values):
        res = super().create(values)
        res.update_product_datasheets(res.ids, delayed=True)
        return res
