# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.lighting.models.product import ES_MAP, D_MAP, C_STATES

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

MIN_STOCK = 10


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
    template_description = '<li style="margin-bottom:0;color:#545454;font-size:small;">%s</li>'

    preview = []
    if title:
        preview.append(template_title % title)
    if url:
        preview.append(template_url % url)
    if description:
        preview.append(template_description % description)

    meta_preview = False
    if preview:
        meta_preview = template % ''.join(preview)

    return meta_preview


class LightingProduct(models.Model):
    _inherit = 'lighting.product'

    website_published = fields.Boolean('Published on Website', copy=False, track_visibility='onchange')

    website_published_readonly = fields.Boolean(compute="_compute_website_published_readonly")

    @api.multi
    def _compute_website_published_readonly(self):
        for rec in self:
            rec.website_published_readonly = not rec.user_has_groups('lighting_seo.group_lighting_ecommerce_manager')

    @api.multi
    def website_publish_button(self):
        self.ensure_one()
        return self.write({'website_published': not self.website_published})

    seo_title = fields.Char(string='Meta title', translate=True)
    seo_url = fields.Char(string='URL')
    seo_description = fields.Text(string='Meta description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword',
                                       relation='lighting_product_seo_keyword_rel',
                                       column1='product_id', column2='keyword_id', string='Keywords')

    meta_title_length = fields.Integer(string='Meta title length', compute='_compute_lengths', readonly=True)
    meta_description_length = fields.Integer(string='Meta description length', compute='_compute_lengths',
                                             readonly=True)

    @api.depends('seo_title', 'seo_description')
    def _compute_lengths(self):
        for rec in self:
            if rec.seo_title:
                rec.meta_title_length = len(rec.seo_title)
            if rec.seo_description:
                rec.meta_description_length = len(rec.seo_description)

    meta_preview = fields.Char(string='Preview', compute='_compute_preview', readonly=True)

    @api.depends('seo_title', 'seo_url', 'seo_description')
    def _compute_preview(self):
        for rec in self:
            rec.meta_preview = seo_preview(rec.seo_title, rec.seo_url, rec.seo_description)

    marketplace_description = fields.Text(string='Marketplace Description', translate=True, track_visibility='onchange')

    @api.constrains('website_published')
    def check_website_published(self):
        for rec in self:
            if rec.website_published and rec.website_published_readonly:
                raise ValidationError("You have no permissions to modify this field")

    def _check_state_marketing_stock(self, values):
        new_values = super(LightingProduct, self)._check_state_marketing_stock(values)
        values.update(new_values)
        current_state, new_state = self.state_marketing, values.get('state_marketing', self.state_marketing)
        current_stock = self.available_qty + self.stock_future_qty
        new_stock = sum([values[f] if f in values else self[f] for f in ('available_qty', 'stock_future_qty')])
        if current_state in C_STATES:
            if new_state in D_MAP:
                self._update_with_check(new_values, 'website_published', False)
        elif current_state in ES_MAP:
            if new_state == current_state:
                if new_stock > current_stock:
                    if new_stock >= MIN_STOCK:
                        self._update_with_check(new_values, 'website_published', True)
            elif new_state == ES_MAP[current_state]:
                self._update_with_check(new_values, 'website_published', False)
        elif current_state in D_MAP:
            if new_state == current_state:
                self._update_with_check(new_values, 'website_published', False)
            elif new_state == D_MAP[current_state]:
                self._update_with_check(new_values, 'website_published', new_stock >= MIN_STOCK)
        return new_values


class LightingProductFamily(models.Model):
    _inherit = 'lighting.product.family'

    seo_title = fields.Char(string='Meta title', translate=True)
    seo_url = fields.Char(string='URL')
    seo_description = fields.Text(string='Meta description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword',
                                       relation='lighting_product_family_seo_keyword_rel',
                                       column1='family_id', column2='keyword_id', string='Keywords')

    meta_title_length = fields.Integer(string='Meta title length', compute='_compute_lengths', readonly=True)
    meta_description_length = fields.Integer(string='Meta description length', compute='_compute_lengths',
                                             readonly=True)

    @api.depends('seo_title', 'seo_description')
    def _compute_lengths(self):
        for rec in self:
            if rec.seo_title:
                rec.meta_title_length = len(rec.seo_title)
            if rec.seo_description:
                rec.meta_description_length = len(rec.seo_description)

    meta_preview = fields.Char(string='Preview', compute='_compute_preview', readonly=True)

    @api.depends('seo_title', 'seo_url', 'seo_description')
    def _compute_preview(self):
        for rec in self:
            rec.meta_preview = seo_preview(rec.seo_title, rec.seo_url, rec.seo_description)


class LightingProductCategory(models.Model):
    _inherit = 'lighting.product.category'

    seo_title = fields.Char(string='Meta title', translate=True)
    seo_url = fields.Char(string='URL')
    seo_description = fields.Char(string='Meta description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword',
                                       relation='lighting_product_category_seo_keyword_rel',
                                       column1='category_id', column2='keyword_id', string='Keywords')

    meta_title_length = fields.Integer(string='Meta title length', compute='_compute_lengths', readonly=True)
    meta_description_length = fields.Integer(string='Meta description length', compute='_compute_lengths',
                                             readonly=True)

    @api.depends('seo_title', 'seo_description')
    def _compute_lengths(self):
        for rec in self:
            if rec.seo_title:
                rec.meta_title_length = len(rec.seo_title)
            if rec.seo_description:
                rec.meta_description_length = len(rec.seo_description)

    meta_preview = fields.Char(string='Preview', compute='_compute_preview', readonly=True)

    @api.depends('seo_title', 'seo_url', 'seo_description')
    def _compute_preview(self):
        for rec in self:
            rec.meta_preview = seo_preview(rec.seo_title, rec.seo_url, rec.seo_description)


class LightingProductApplication(models.Model):
    _inherit = 'lighting.product.application'

    seo_title = fields.Char(string='Meta title', translate=True)
    seo_url = fields.Char(string='URL')
    seo_description = fields.Char(string='Meta description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword',
                                       relation='lighting_product_application_seo_keyword_rel',
                                       column1='application_id', column2='keyword_id', string='Keywords')

    meta_title_length = fields.Integer(string='Meta title length', compute='_compute_lengths', readonly=True)
    meta_description_length = fields.Integer(string='Meta description length', compute='_compute_lengths',
                                             readonly=True)

    @api.depends('seo_title', 'seo_description')
    def _compute_lengths(self):
        for rec in self:
            if rec.seo_title:
                rec.meta_title_length = len(rec.seo_title)
            if rec.seo_description:
                rec.meta_description_length = len(rec.seo_description)

    meta_preview = fields.Char(string='Preview', compute='_compute_preview', readonly=True)

    @api.depends('seo_title', 'seo_url', 'seo_description')
    def _compute_preview(self):
        for rec in self:
            rec.meta_preview = seo_preview(rec.seo_title, rec.seo_url, rec.seo_description)


class LightingCatalog(models.Model):
    _inherit = 'lighting.catalog'

    seo_title = fields.Char(string='Meta title', translate=True)
    seo_url = fields.Char(string='URL')
    seo_description = fields.Char(string='Meta description', translate=True)
    seo_keyword_ids = fields.Many2many(comodel_name='lighting.seo.keyword',
                                       relation='lighting_catalog_seo_keyword_rel',
                                       column1='catalog_id', column2='keyword_id', string='Keywords')
    meta_title_length = fields.Integer(string='Meta title length', compute='_compute_lengths', readonly=True)
    meta_description_length = fields.Integer(string='Meta description length', compute='_compute_lengths',
                                             readonly=True)

    @api.depends('seo_title', 'seo_description')
    def _compute_lengths(self):
        for rec in self:
            if rec.seo_title:
                rec.meta_title_length = len(rec.seo_title)
            if rec.seo_description:
                rec.meta_description_length = len(rec.seo_description)

    meta_preview = fields.Char(string='Preview', compute='_compute_preview', readonly=True)

    @api.depends('seo_title', 'seo_url', 'seo_description')
    def _compute_preview(self):
        for rec in self:
            rec.meta_preview = seo_preview(rec.seo_title, rec.seo_url, rec.seo_description)
