# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


def seo_preview(title, url, description):
    template = """
        <div style="font-family:arial,sans-serif;max-width:600px;">
            <ul class="list-unstyled">
                %s
            </ul>
        </div >
    """
    template_title = '<li style="margin-bottom:0;color:#1a0dab;font-size:18px;">%s</li>'
    template_url = '<li style="margin-bottom:0;color:#006621;font-size:14px;">%s</li>'
    template_description = (
        '<li style="margin-bottom:0;color:#545454;font-size:small;">%s</li>'
    )

    preview = []
    if title:
        preview.append(template_title % title)
    if url:
        preview.append(template_url % url)
    if description:
        preview.append(template_description % description)

    meta_preview = False
    if preview:
        meta_preview = template % "".join(preview)

    return meta_preview


class LightingSeoMixin(models.AbstractModel):
    _name = "lighting.seo.mixin"
    _description = "SEO Mixin"

    seo_title = fields.Char(
        string="Meta title",
        translate=True,
    )
    seo_url = fields.Char(
        string="URL",
    )
    seo_description = fields.Text(
        string="Meta description",
        translate=True,
    )
    seo_keyword_ids = fields.Many2many(
        string="Keywords",
        comodel_name="lighting.seo.keyword",
    )
    meta_title_length = fields.Integer(
        compute="_compute_lengths",
    )
    meta_description_length = fields.Integer(
        compute="_compute_lengths",
    )

    # TODO: Try this change
    @api.depends("seo_title", "seo_description")
    def _compute_lengths(self):
        for rec in self:
            rec.meta_title_length = len(rec.seo_title) if rec.seo_title else 0
            rec.meta_description_length = (
                len(rec.seo_description) if rec.seo_description else 0
            )
            # if rec.seo_title:
            #     rec.meta_title_length = len(rec.seo_title)
            # if rec.seo_description:
            #     rec.meta_description_length = len(rec.seo_description)

    meta_preview = fields.Char(
        string="Preview",
        compute="_compute_preview",
    )

    @api.depends("seo_title", "seo_url", "seo_description")
    def _compute_preview(self):
        for rec in self:
            rec.meta_preview = seo_preview(
                rec.seo_title, rec.seo_url, rec.seo_description
            )
