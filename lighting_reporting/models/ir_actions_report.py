# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import base64
import io

from PyPDF2 import PdfFileReader, PdfFileWriter

from odoo import api, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.multi
    def render_qweb_pdf(self, res_ids=None, data=None):
        def close_streams(streams):
            for stream in streams:
                try:
                    stream.close()
                except Exception:
                    pass

        result = super(IrActionsReport, self).render_qweb_pdf(
            res_ids=res_ids, data=data
        )

        if self.report_name == "lighting_reporting.report_product":
            pdf_content, file_type = result
            if pdf_content:
                model, res_ids = data["model"], data["ids"]

                res_ids_map = {}
                for i, res_id in enumerate(res_ids):
                    attachs = (
                        self.env[model]
                        .browse(res_id)
                        .attachment_ids.filtered(
                            lambda x: x.type_id.include_in_datasheet
                        )
                        .sorted("sequence")
                    )
                    if attachs:
                        res_ids_map[i] = attachs
                if not res_ids_map:
                    return result

                streams = []
                pdf_content_stream = io.BytesIO(pdf_content)
                reader = PdfFileReader(pdf_content_stream)
                root = reader.trailer["/Root"]
                if "/Outlines" in root and "/First" in root["/Outlines"]:
                    outlines_pages = []
                    node = root["/Outlines"]["/First"]
                    while True:
                        outlines_pages.append(root["/Dests"][node["/Dest"]][0])
                        if "/Next" not in node:
                            break
                        node = node["/Next"]
                    outlines_pages = sorted(set(outlines_pages))
                    # There should be only one top-level heading by document
                    assert len(outlines_pages) == len(res_ids)
                    # There should be a top-level heading on first page
                    assert outlines_pages[0] == 0
                    for i, num in enumerate(outlines_pages):
                        to = (
                            outlines_pages[i + 1]
                            if i + 1 < len(outlines_pages)
                            else reader.numPages
                        )
                        writer = PdfFileWriter()
                        for j in range(num, to):
                            writer.addPage(reader.getPage(j))

                        streams_to_close = []
                        for ad in res_ids_map.get(i, []):
                            addt_content_stream = io.BytesIO(
                                base64.decodebytes(ad.datas)
                            )
                            streams_to_close.append(addt_content_stream)
                            addt_reader = PdfFileReader(addt_content_stream)
                            writer.appendPagesFromReader(addt_reader)
                        stream = io.BytesIO()
                        writer.write(stream)
                        streams.append(stream)
                        close_streams(streams_to_close)

                close_streams([pdf_content_stream])

                # Build the final pdf.
                writer = PdfFileWriter()
                for stream in streams:
                    reader = PdfFileReader(stream)
                    writer.appendPagesFromReader(reader)
                result_stream = io.BytesIO()
                streams.append(result_stream)
                writer.write(result_stream)
                result_value = result_stream.getvalue()
                # We have to close the streams after PdfFileWriter's call to write()
                close_streams(streams)

                return result_value, "pdf"

        return result
