# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class LightingProductBeam(models.Model):
    _name = "lighting.product.beam"
    _description = "Product Beam"
    _order = "sequence"

    sequence = fields.Integer(
        required=True,
        default=1,
        help="The sequence field is used to define order",
    )
    num = fields.Integer(
        string="Number of beams",
        required=True,
        default=1,
    )
    photometric_distribution_ids = fields.Many2many(
        comodel_name="lighting.product.beam.photodistribution",
        relation="lighting_product_beam_photodistribution_rel",
    )
    dimension_ids = fields.One2many(
        comodel_name="lighting.product.beam.dimension",
        inverse_name="beam_id",
        string="Dimensions",
        copy=True,
    )
    product_id = fields.Many2one(
        comodel_name="lighting.product",
        ondelete="cascade",
    )

    # computed fields
    dimensions_display = fields.Char(
        compute="_compute_dimensions_display",
        string="Dimensions",
    )

    @api.depends("dimension_ids")
    def _compute_dimensions_display(self):
        for rec in self:
            rec.dimensions_display = rec.dimension_ids.get_display()

    # aux display functions
    def get_beam_photometric_distribution(self):
        res = []
        for rec in self.sorted(lambda x: x.sequence):
            if rec.photometric_distribution_ids:
                res.append(
                    ", ".join(
                        [x.display_name for x in rec.photometric_distribution_ids]
                    )
                )

        if not any(res):
            return None
        return res

    def get_beam(self):
        res = []
        for rec in self.sorted(lambda x: x.sequence):
            bm = []
            if rec.num > 1:
                bm.append("%ix" % rec.num)

            if rec.photometric_distribution_ids:
                bm.append(rec.get_beam_photometric_distribution()[0])

            dimension_display = rec.dimension_ids.get_display()
            if dimension_display:
                bm.append(dimension_display)

            if bm:
                res.append(" ".join(bm))

        if not any(res):
            return None
        return res

    def get_beam_angle(self):
        res = []
        for src in self.sorted(lambda x: x.sequence):
            angl = []
            for d in src.dimension_ids.sorted(lambda x: x.sequence):
                if d.value and d.type_id.uom == "º":
                    angl.append("%g%s" % (d.value, d.type_id.uom))
            ang_v = None
            if angl:
                ang_v = "/".join(angl)
            res.append(ang_v)

        if not any(res):
            return None
        return res

    def get_beam_angle_display(self, spaces=False):
        value_display = False
        beam_angle = self.get_beam_angle()
        if beam_angle:
            separator = spaces and ", " or ","
            value_display = separator.join(filter(None, beam_angle))
        return value_display
