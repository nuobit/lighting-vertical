# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.tests import common
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TestProduct(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProduct, cls).setUpClass()

    def test_state_marketing_es_with_stock(self):
        """
            Test state marketing and stock consistency
        """
        # ARRANGE
        c1 = self.env['lighting.product.category'].create({
            'name': 'Category 1',
            'code': 'CAT1'
        })
        p1 = self.env['lighting.product'].create({
            'reference': 'REF1',
            'category_id': c1.id,
        })

        # ACT & ASSERT
        assert_validationerror = lambda x, y: self.assertRaises(ValidationError, x, y)
        tests = [
            {'arrange': {'state_marketing': 'ES', 'available_qty': 0, 'stock_future_qty': 1},
             'actassert': lambda x: assert_validationerror(x.write, {'state_marketing': 'D'}),
             },
            {'arrange': {'state_marketing': 'ES', 'available_qty': 1, 'stock_future_qty': 0},
             'actassert': lambda x: assert_validationerror(x.write, {'state_marketing': 'D'}),
             },
            {'arrange': {'state_marketing': 'ES', 'available_qty': 1, 'stock_future_qty': 1},
             'actassert': lambda x: assert_validationerror(x.write, {'state_marketing': 'D'}),
             },
            {'arrange': {'state_marketing': 'ES', 'available_qty': 0, 'stock_future_qty': 1},
             'actassert': lambda x: assert_validationerror(x.write, {'state_marketing': 'H'}),
             },
            {'arrange': {'state_marketing': 'ES', 'available_qty': 1, 'stock_future_qty': 0},
             'actassert': lambda x: assert_validationerror(x.write, {'state_marketing': 'H'}),
             },
            {'arrange': {'state_marketing': 'ES', 'available_qty': 1, 'stock_future_qty': 1},
             'actassert': lambda x: assert_validationerror(x.write, {'state_marketing': 'H'}),
             },

            {'actassert': lambda x: assert_validationerror(
                x.write, {'state_marketing': 'D', 'available_qty': 0, 'stock_future_qty': 1}),
             },
            {'actassert': lambda x: assert_validationerror(
                x.write, {'state_marketing': 'D', 'available_qty': 1, 'stock_future_qty': 0}),
             },
            {'actassert': lambda x: assert_validationerror(
                x.write, {'state_marketing': 'D', 'available_qty': 1, 'stock_future_qty': 1}),
             },
            {'actassert': lambda x: assert_validationerror(
                x.write, {'state_marketing': 'H', 'available_qty': 0, 'stock_future_qty': 1}),
             },
            {'actassert': lambda x: assert_validationerror(
                x.write, {'state_marketing': 'H', 'available_qty': 1, 'stock_future_qty': 0}),
             },
            {'actassert': lambda x: assert_validationerror(
                x.write, {'state_marketing': 'H', 'available_qty': 1, 'stock_future_qty': 1}),
             },

            {'arrange': {'state_marketing': 'ES', 'available_qty': 1, 'stock_future_qty': 1},
             'act': lambda x: x.write({'available_qty': 0}),
             'assert': lambda x: self.assertEqual(
                 x.state_marketing, 'ES', "The state marketing has changed and it shouldn't"),
             },
            {'arrange': {'state_marketing': 'ES', 'available_qty': 1, 'stock_future_qty': 1},
             'act': lambda x: x.write({'stock_future_qty': 0}),
             'assert': lambda x: self.assertEqual(
                 x.state_marketing, 'ES', "The state marketing has changed and it shouldn't"),
             },
            {'arrange': {'state_marketing': 'ES', 'available_qty': 1, 'stock_future_qty': 1},
             'act': lambda x: x.write({'available_qty': 0, 'stock_future_qty': 0}),
             'assert': lambda x: self.assertEqual(
                 x.state_marketing, 'D',
                 "The state marketing has not changed and it should have changed to discontinued (D)"),
             },

            {'act': lambda x: x.write({'state_marketing': 'D', 'available_qty': 0, 'stock_future_qty': 0}),
             'assert': lambda x: self.assertEqual(
                 x.state_marketing, 'D', "The state marketing has changed and it shouldn't"),
             },
            {'act': lambda x: x.write({'state_marketing': 'H', 'available_qty': 0, 'stock_future_qty': 0}),
             'assert': lambda x: self.assertEqual(
                 x.state_marketing, 'H', "The state marketing has changed and it shouldn't"),
             },

            {'arrange': {'state_marketing': 'C', 'available_qty': 1, 'stock_future_qty': 1},
             'act': lambda x: x.write({'available_qty': 0, 'stock_future_qty': 0}),
             'assert': lambda x: self.assertEqual(
                 x.state_marketing, 'C',
                 "The state marketing has changed and it shouldn't"),
             },
            {'act': lambda x: x.write({'state_marketing': 'C', 'available_qty': 0, 'stock_future_qty': 0}),
             'assert': lambda x: self.assertEqual(
                 x.state_marketing, 'C',
                 "The state marketing has changed and it shouldn't"),
             },
        ]
        for t in tests:
            if 'arrange' in t:
                p1.write(t['arrange'])
            if 'act' in t:
                t['act'](p1)
            with self.subTest():
                t.get('assert', t.get('actassert'))(p1)
