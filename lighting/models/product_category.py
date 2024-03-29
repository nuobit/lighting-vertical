# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LightingProductCategory(models.Model):
    _name = "lighting.product.category"
    _description = "Product Category"
    _inherit = ["lighting.tree.mixin", "mail.thread", "mail.activity.mixin"]
    _parent_name = "parent_id"
    _order = "sequence,name"

    def name_get(self):
        vals = []
        for record in self:
            vals.append((record.id, record.complete_name))
        return vals

    @api.model
    def _get_domain(self):
        model_id = self.env.ref("lighting.model_lighting_product").id
        return [("model_id", "=", model_id)]

    code = fields.Char(
        size=5,
        required=True,
    )
    name = fields.Char(
        required=True,
        translate=True,
    )

    parent_id = fields.Many2one(
        comodel_name="lighting.product.category",
        index=True,
        ondelete="cascade",
        tracking=True,
    )
    child_ids = fields.One2many(
        comodel_name="lighting.product.category",
        inverse_name="parent_id",
        string="Child Categories",
        tracking=True,
    )

    root_id = fields.Many2one(
        comodel_name="lighting.product.category",
        readonly=True,
        compute="_compute_root",
    )

    def _compute_root(self):
        for rec in self:
            rec.root_id = rec._get_root()

    is_accessory = fields.Boolean()
    sequence = fields.Integer(
        required=True,
        default=1,
        help="The sequence field is used to define order",
    )

    # description
    description_text = fields.Char(
        help="Text to show on a generated product description",
        translate=True,
    )
    description_dimension_ids = fields.Many2many(
        string="Description Dimensions",
        comodel_name="lighting.dimension.type",
        relation="lighting_category_dimension_type_rel",
        column1="category_id",
        column2="dimension_type_id",
    )
    inherit_description_dimensions = fields.Boolean()
    effective_description_dimension_ids = fields.Many2many(
        comodel_name="lighting.dimension.type",
        string="Effective Description Dimensions",
        readonly=True,
        compute="_compute_effective_description_dimension_ids",
    )

    def _get_parents_description_dimensions(self):
        self.ensure_one()
        if not self.inherit_description_dimensions:
            return self.description_dimension_ids
        else:
            if not self.parent_id:
                return self.description_dimension_ids
            else:
                return (
                    self.description_dimension_ids
                    | self.parent_id._get_parents_description_dimensions()
                )

    @api.depends(
        "inherit_description_dimensions", "description_dimension_ids", "parent_id"
    )
    def _compute_effective_description_dimension_ids(self):
        for rec in self:
            rec.effective_description_dimension_ids = (
                rec._get_parents_description_dimensions()
            )

    # attributes
    attribute_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        relation="lighting_product_category_field_attribute_rel",
        column1="category_id",
        column2="field_id",
        domain=_get_domain,
        string="Attributes",
    )

    inherit_attributes = fields.Boolean()
    effective_attribute_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        string="Effective attributes",
        readonly=True,
        compute="_compute_effective_attributes",
    )

    def _get_parents_attributes(self):
        self.ensure_one()
        if not self.inherit_attributes:
            return self.attribute_ids
        else:
            if not self.parent_id:
                return self.attribute_ids
            else:
                return self.attribute_ids | self.parent_id._get_parents_attributes()

    def _compute_effective_attributes(self):
        for rec in self:
            rec.effective_attribute_ids = rec._get_parents_attributes()

    # TODO: Modificar el onchange, deberia calcularse
    #  solo si inherit attributes es True? modificar el compute
    @api.onchange("inherit_attributes", "attribute_ids")
    def onchange_attribute_ids(self):
        if self.inherit_attributes:
            self._compute_effective_attributes()

    # fields
    field_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        relation="lighting_product_category_field_field_rel",
        column1="category_id",
        column2="field_id",
        domain=_get_domain,
        string="Fields",
    )

    inherit_fields = fields.Boolean()
    effective_field_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        string="Effective fields",
        readonly=True,
        compute="_compute_effective_fields",
    )

    def _get_parents_fields(self):
        self.ensure_one()
        if not self.inherit_fields:
            return self.field_ids
        else:
            if not self.parent_id:
                return self.field_ids
            else:
                return self.field_ids | self.parent_id._get_parents_fields()

    def _compute_effective_fields(self):
        for rec in self:
            rec.effective_field_ids = rec._get_parents_fields()

    # TODO: Modificar el onchange, deberia calcularse
    #  solo si inherit fields es True? modificar el compute
    @api.onchange("inherit_fields", "field_ids")
    def onchange_field_ids(self):
        if self.inherit_fields:
            self._compute_effective_fields()

    # products
    product_ids = fields.One2many(
        comodel_name="lighting.product",
        inverse_name="category_id",
        string="Products",
    )

    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
    )

    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec.product_ids)

    flat_product_ids = fields.Many2many(
        comodel_name="lighting.product",
        compute="_compute_flat_products",
    )

    def _get_flat_products(self):
        self.ensure_one()
        if not self.child_ids:
            return self.product_ids
        else:
            products = self.env["lighting.product"]
            for ch in self.child_ids:
                products += ch._get_flat_products()
            return products

    def _compute_flat_products(self):
        for rec in self:
            rec.flat_product_ids = rec._get_flat_products()

    flat_product_count = fields.Integer(
        compute="_compute_flat_product_count",
        string="Products (flat)",
    )

    def _compute_flat_product_count(self):
        for rec in self:
            rec.flat_product_count = len(rec.flat_product_ids)

    attachment_ids = fields.One2many(
        comodel_name="lighting.product.category.attachment",
        inverse_name="category_id",
        string="Attachments",
        copy=True,
        tracking=True,
    )
    attachment_count = fields.Integer(
        compute="_compute_attachment_count",
        string="Attachment(s)",
    )

    @api.depends("attachment_ids")
    def _compute_attachment_count(self):
        for rec in self:
            rec.attachment_count = len(rec.attachment_ids)

    _sql_constraints = [
        ("name_uniq", "unique (parent_id,name)", "The type must be unique by parent!"),
        ("code_uniq", "unique (code)", "The code must be unique!"),
    ]

    @api.constrains("is_accessory")
    def _check_efficiency_lampholder(self):
        for rec in self:
            lamp_eff_products = rec.product_ids.filtered(
                lambda x: (
                    x.source_ids.mapped("lampholder_id")
                    or x.source_ids.mapped("lampholder_technical_id")
                )
                and x.source_ids.mapped("line_ids.efficiency_ids")
            )
            if not rec._get_is_accessory() and lamp_eff_products:
                raise ValidationError(
                    _(
                        "A non accessory source with lampholder cannot have efficiency: %s"
                    )
                    % (lamp_eff_products.sorted("reference").mapped("reference"))
                )

    def _get_is_accessory(self):
        self.ensure_one()
        if self.is_accessory:
            return True
        if not self.parent_id:
            return self.is_accessory
        return self.parent_id._get_is_accessory()

    def action_child(self):
        return {
            "name": _("Childs of %s") % self.complete_name,
            "type": "ir.actions.act_window",
            "res_model": "lighting.product.category",
            "views": [(False, "tree"), (False, "form")],
            "domain": [("id", "in", self.child_ids.mapped("id"))],
            "context": {"default_parent_id": self.id},
        }

    def action_flat_product(self):
        return {
            "name": _("Flat products below %s") % self.complete_name,
            "type": "ir.actions.act_window",
            "res_model": "lighting.product",
            "views": [(False, "tree"), (False, "form")],
            "domain": [("id", "in", self.flat_product_ids.mapped("id"))],
            "context": {"default_category_id": self.id},
        }
