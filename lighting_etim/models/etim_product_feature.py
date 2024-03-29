# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

VALUE_DETAIL_HELP = """With this field more precise information
on the color of a product defined in the ETIM model can be made avail-
able if necessary and useful. Especially in the product range of Domestic
switching devices, Luminaries, Cable ducts or Small
household appliances the indication is important and should be transmitted
by the manufacturer in the ETIM BMEcat.
So here are meant all alphanumeric features in ETIM that have the word
"colour" (or "color") in their names.
e.g. Color of a cover frame for domestic switching devices
<FEATURE>
<FNAME>EF000007</FNAME>
<FVALUE>EV000080</FVALUE>
<FVALUE_DETAILS>azure blue</FVALUE_DETAILS>
</FEATURE>
EF000007 = "Colour"
EV000080 = "Blue"
"""


class LightingProductETIMFeature(models.Model):
    _name = "lighting.etim.product.feature"
    _order = "feature_code"

    feature_id = fields.Many2one(
        comodel_name="lighting.etim.feature",
        ondelete="restrict",
        string="Feature",
        required=True,
    )
    feature_code = fields.Char(
        related="feature_id.code",
        readonly=True,
        store=True,
    )

    @api.onchange("feature_id")
    def feature_id_change(self):
        self.unit_id = self.product_id.class_id.feature_ids.filtered(
            lambda x: x["feature_id"] == self.feature_id
        ).unit_id
        feature_value_ids = self.product_id.class_id.feature_ids.filtered(
            lambda x: x["feature_id"] == self.feature_id
        ).value_ids.mapped("value_id.id")

        return {
            "domain": {
                "unit_id": [("id", "=", self.unit_id.id)],
                "a_value_id": [("id", "in", feature_value_ids)],
            },
        }

    feature_type = fields.Selection(
        string="Type",
        related="feature_id.type",
        readonly=True,
    )
    unit_id = fields.Many2one(
        comodel_name="lighting.etim.unit",
        ondelete="restrict",
        readonly=True,
    )
    has_unit = fields.Boolean(
        compute="_compute_has_unit",
    )

    @api.depends("feature_id")
    def _compute_has_unit(self):
        for rec in self:
            unit_ids = rec.product_id.class_id.feature_ids.filtered(
                lambda x: x["feature_id"] == rec.feature_id
            ).unit_id
            rec.has_unit = len(unit_ids) != 0

    a_value_id = fields.Many2one(
        string="Value",
        comodel_name="lighting.etim.value",
        ondelete="restrict",
    )
    l_value = fields.Boolean(
        string="Value",
    )
    n_value = fields.Float(
        string="Value",
    )
    r1_value = fields.Float(
        string="Value 1",
    )
    r2_value = fields.Float(
        string="Value 2",
    )

    value = fields.Json(
        compute="_compute_value",
        inverse="_inverse_value",
    )

    @api.depends(
        "feature_id", "a_value_id", "l_value", "n_value", "r1_value", "r2_value"
    )
    def _compute_value(self):
        for rec in self:
            if rec.feature_id.type == "A":
                rec.value = rec.a_value_id.id
            elif rec.feature_id.type == "L":
                rec.value = rec.l_value
            elif rec.feature_id.type == "N":
                rec.value = rec.n_value
            elif rec.feature_id.type == "R":
                rec.value = [rec.r1_value, rec.r2_value]
            else:
                raise ValidationError(_("Type %s not valid!") % rec.feature_id.type)

    def _inverse_value(self):
        for rec in self:
            if rec.feature_id.type == "A":
                rec.a_value_id = rec.value
            elif rec.feature_id.type == "L":
                rec.l_value = rec.value
            elif rec.feature_id.type == "N":
                rec.n_value = rec.value
            elif rec.feature_id.type == "R":
                rec.r1_value, rec.r2_value = rec.value
            else:
                raise ValidationError(_("Type %s not valid!") % rec.feature_id.type)

    unassignable = fields.Boolean(
        default=False,
    )
    ua_value_detail = fields.Selection(
        string="Value detail",
        selection=[
            ("NA", _("Not applicable")),
            ("MV", _("Missing value")),
            ("UN", _("Unknown")),
        ],
        help="NA - Not applicable (this feature is not applicable "
        "in the context of a product in this class)\n"
        "MV - Missing value (an alphanumeric feature is relevant, "
        "but no correct value exists in this ETIM version)\n"
        "UN - Unknown (currently, the data supplier is not able "
        "to deliver a specific value; but basically it is possible)",
    )

    value_detail = fields.Char(
        help=VALUE_DETAIL_HELP,
    )
    value_str = fields.Char(
        string="Value",
        compute="_compute_value_str",
        readonly=True,
    )

    @api.depends("value")
    def _compute_value_str(self):
        for rec in self:
            if rec.feature_id.type == "A":
                rec.value_str = (
                    self.env["lighting.etim.value"].browse(rec.value).display_name
                )
            elif rec.feature_id.type == "L":
                rec.value_str = str(rec.value)
            elif rec.feature_id.type == "N":
                rec.value_str = str(rec.value)
            elif rec.feature_id.type == "R":
                range_str = [str(x) for x in rec.value]
                if range_str:
                    rec.value_str = " - ".join(range_str)
            else:
                rec.value_str = False

    product_class_id = fields.Many2one(
        related="product_id.class_id",
        readonly=True,
    )
    product_class_feature_ids = fields.One2many(
        comodel_name="lighting.etim.feature",
        compute="_compute_product_class_feature_ids",
        readonly=True,
    )

    @api.depends("product_class_id")
    def _compute_product_class_feature_ids(self):
        for rec in self:
            rec.product_class_feature_ids = rec.product_id.class_id.feature_ids.mapped(
                "feature_id"
            )

    product_id = fields.Many2one(
        comodel_name="lighting.product",
        ondelete="cascade",
        required=True,
    )

    _sql_constraints = [
        ("feature_uniq", "unique (feature_id, product_id)", "Feature duplicated"),
    ]
