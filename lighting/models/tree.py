# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingTreeMixin(models.AbstractModel):
    _name = 'lighting.tree.mixin'

    # complete_name
    complete_name = fields.Char('Complete Name',
                                compute='_compute_complete_name',
                                search='_search_complete_name')

    def get_complete_name(self):
        self.ensure_one()

        def get_node_ancestors_chain(parent_id, child_ids):
            if not parent_id:
                return child_ids
            else:
                return get_node_ancestors_chain(parent_id.parent_id, parent_id | child_ids)

        return ' / '.join(
            get_node_ancestors_chain(self, self.env[self._name]).mapped('name')
        )

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for rec in self:
            if rec.parent_id:
                rec.complete_name = '%s / %s' % (rec.parent_id.complete_name, rec.name)
            else:
                rec.complete_name = rec.name

    def _search_complete_name(self, operator, value):
        node_ids = []
        for node in self.env[self._name].search([]):
            complete_name = node.get_complete_name()
            if operator == '=':
                if value == complete_name:
                    node_ids.append(node.id)
            elif operator == '!=':
                if value != complete_name:
                    node_ids.append(node.id)
            elif operator == 'like':
                if value in complete_name:
                    node_ids.append(node.id)
            elif operator == 'not like':
                if value not in complete_name:
                    node_ids.append(node.id)
            elif operator == 'ilike':
                if value.lower() in complete_name.lower():
                    node_ids.append(node.id)
            elif operator == 'not ilike':
                if value.lower() not in complete_name.lower():
                    node_ids.append(node.id)
            elif operator == '=like':
                if value == complete_name:
                    node_ids.append(node.id)
            elif operator == '=ilike':
                if value.lower() == complete_name.lower():
                    node_ids.append(node.id)
            else:
                raise UserError(_("Operator %s not implemented") % operator)

        return [('id', 'in', node_ids)]

    @api.model
    def get_leaf_from_complete_name(self, complete_name):
        def complete_name_to_leaf(parent, childs):
            if not childs:
                return parent
            else:
                nodes = self.env[self._name].search([
                    ('parent_id', '=', parent.id),
                    ('name', '=', childs[0]),
                ])
                leafs = self.env[self._name]
                for node in nodes:
                    leafs += complete_name_to_leaf(node, childs[1:])

                return leafs

        return complete_name_to_leaf(self.env[self._name],
                                     complete_name.split(' / '))

    # childs
    child_count = fields.Integer(compute='_compute_child_count', string='Childs')

    def _compute_child_count(self):
        for rec in self:
            rec.child_count = len(rec.child_ids)

    # level
    level = fields.Integer(string='Level', readonly=True, compute='_compute_level')

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
