# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class LightingTreeMixin(models.AbstractModel):
    _name = "lighting.tree.mixin"

    # complete_name
    complete_name = fields.Char(
        "Complete Name",
        compute="_compute_complete_name",
        search="_search_complete_name",
    )

    complete_chain_ids = fields.Many2many(
        string="Complete Chain",
        comodel_name="lighting.product.category",
        compute="_compute_complete_chain_ids",
    )

    def _get_node_ancestors_chain(self):
        self.ensure_one()
        return (
            self.parent_id
            and self.parent_id._get_node_ancestors_chain()
            or self.env[self._name]
        ) | self

    @api.depends("parent_id")
    def _compute_complete_chain_ids(self):
        for rec in self:
            rec.complete_chain_ids = rec._get_node_ancestors_chain()

    def get_complete_name(self):
        self.ensure_one()
        return " / ".join(self.complete_chain_ids.mapped("name"))

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for rec in self:
            if rec.parent_id:
                rec.complete_name = "%s / %s" % (rec.parent_id.complete_name, rec.name)
            else:
                rec.complete_name = rec.name

    def _search_complete_name(self, operator, value):
        node_ids = []
        for node in self.env[self._name].search([]):
            complete_name = node.get_complete_name()
            if operator == "=":
                if value == complete_name:
                    node_ids.append(node.id)
            elif operator == "!=":
                if value != complete_name:
                    node_ids.append(node.id)
            elif operator == "like":
                if value in complete_name:
                    node_ids.append(node.id)
            elif operator == "not like":
                if value not in complete_name:
                    node_ids.append(node.id)
            elif operator == "ilike":
                if value.lower() in complete_name.lower():
                    node_ids.append(node.id)
            elif operator == "not ilike":
                if value.lower() not in complete_name.lower():
                    node_ids.append(node.id)
            elif operator == "=like":
                if value == complete_name:
                    node_ids.append(node.id)
            elif operator == "=ilike":
                if value.lower() == complete_name.lower():
                    node_ids.append(node.id)
            else:
                raise UserError(_("Operator %s not implemented") % operator)

        return [("id", "in", node_ids)]

    @api.model
    def get_leaf_from_complete_name(self, complete_name):
        def complete_name_to_leaf(parent, childs):
            if not childs:
                return parent
            else:
                nodes = self.env[self._name].search(
                    [
                        ("parent_id", "=", parent.id),
                        ("name", "=", childs[0]),
                    ]
                )
                leafs = self.env[self._name]
                for node in nodes:
                    leafs += complete_name_to_leaf(node, childs[1:])

                return leafs

        return complete_name_to_leaf(self.env[self._name], complete_name.split(" / "))

    # childs
    child_count = fields.Integer(compute="_compute_child_count", string="Childs")

    def _compute_child_count(self):
        for rec in self:
            rec.child_count = len(rec.child_ids)

    # level
    level = fields.Integer(string="Level", readonly=True, compute="_compute_level")

    def _get_level(self):
        self.ensure_one()
        if not self.parent_id:
            return 0
        else:
            return self.parent_id._get_level() + 1

    def _compute_level(self):
        for rec in self:
            rec.level = rec._get_level()

    # root
    def _get_root(self):
        self.ensure_one()
        if not self.parent_id:
            return self
        else:
            return self.parent_id._get_root()

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_("Error ! You cannot create recursive categories."))
