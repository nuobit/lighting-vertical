# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LightingProductDimensionAbstract(models.AbstractModel):
    _name = "lighting.product.dimension.abstract"
    _description = "Product Dimension Abstract"
    _rec_name = "type_id"
    _order = "sequence"

    type_id = fields.Many2one(
        comodel_name="lighting.dimension.type",
        ondelete="restrict",
        string="Dimension",
        required=True,
    )
    value = fields.Float(
        required=True,
    )
    sequence = fields.Integer(
        required=True,
        default=1,
        help="The sequence field is used to define order "
        "in which the dimension lines are sorted",
    )

    def get_value_display(self, spaces=True):
        res = []
        for rec in self:
            data = ["%g" % rec.value]
            if rec.type_id.uom:
                data.append(rec.type_id.uom)
            res.append("".join(data))
        separator = spaces and ", " or ","
        return res and separator.join(res) or False

    def get_display(self):
        if self:
            records = self.sorted(
                key=lambda r: (
                    r.sequence,
                    r.id if not isinstance(r.id, models.NewId) else r._origin.id,
                )
            )
            same_uom = True
            uoms = set()
            for rec in records:
                if rec.type_id.uom not in uoms:
                    if not uoms:
                        uoms.add(rec.type_id.uom)
                    else:
                        same_uom = False
                        break

            res_label = " x ".join(["%s" % x.type_id.name for x in records])
            res_value = " x ".join(["%g" % x.value for x in records])

            if same_uom:
                res_label = "%s (%s)" % (res_label, uoms.pop())
            else:
                res_value = " x ".join(
                    ["%g%s" % (x.value, x.type_id.uom) for x in records]
                )

            return "%s: %s" % (res_label, res_value)

        return False

    @api.constrains("value")
    def _check_value(self):
        for rec in self:
            if rec.value <= 0:
                raise ValidationError(
                    _("The value of the dimension %s must be greater than 0")
                    % rec.type_id.name
                )
