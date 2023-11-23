# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LightingProductVoltage(models.Model):
    _name = "lighting.product.voltage"
    _description = "Product Voltage"
    _order = "name"

    name = fields.Char(
        compute="_compute_name",
        string="Voltage",
        required=True,
    )

    @api.depends("voltage1", "voltage2", "voltage2_check", "current_type")
    def _compute_name(self):
        for rec in self:
            voltage_l = []
            if rec.voltage1 != 0:
                voltage_l.append("%g" % rec.voltage1)
            if rec.voltage2_check and rec.voltage2 != 0:
                voltage_l.append("-%g" % rec.voltage2)
            if voltage_l:
                voltage_l.append("V")
            if rec.current_type:
                voltage_l.append(" %s" % rec.current_type)
            if voltage_l:
                rec.name = "".join(voltage_l)

    voltage1 = fields.Float(
        string="Voltage 1 (V)",
        required=True,
    )
    voltage2_check = fields.Boolean(
        string="Voltage 2 check",
    )
    voltage2 = fields.Float(
        string="Voltage 2 (V)",
        default=None,
        compute="_compute_voltage2",
        store=True,
        readonly=False,
    )

    @api.depends("voltage2_check")
    def _compute_voltage2(self):
        for rec in self:
            if not rec.voltage2_check:
                rec.voltage2 = False

    @api.constrains("voltage1", "voltage2", "voltage2_check")
    def _check_voltages(self):
        for rec in self:
            if rec.voltage1 == 0:
                raise ValidationError(_("Voltage 1 cannot be 0"))
            if rec.voltage2_check and rec.voltage2 == 0:
                raise ValidationError(_("Voltage 2 cannot be 0"))

    current_type = fields.Selection(
        selection=[("AC", "Alternating"), ("DC", "Direct")],
        string="Current type",
        required=True,
    )
    product_count = fields.Integer(
        compute="_compute_product_count",
        string="Product(s)",
    )

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env["lighting.product"].search_count(
                [
                    "|",
                    ("input_voltage_id", "=", record.id),
                    ("output_voltage_id", "=", record.id),
                ]
            )

    _sql_constraints = [
        (
            "voltage_uniq",
            "unique (voltage1, voltage2, voltage2_check, current_type)",
            "It already exists another voltage with the same parameters",
        ),
    ]
