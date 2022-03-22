# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.tests import common
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

MIN_QTY = 10


class TestProduct(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProduct, cls).setUpClass()

    def test_state_marketing_es_esh_with_stock(self):
        """
            Test state marketing and stock consistency
        """
        # ARRANGE
        c1 = self.env['lighting.product.category'].create({
            'name': 'Category 1',
            'code': 'CAT1'
        })

        # ACT & ASSERT
        assert_validationerror = lambda x, y: self.assertRaises(ValidationError, x, y)
        tests = [
            {'arrange': {'state_marketing': 'ES', 'available_qty': 0, 'stock_future_qty': MIN_QTY},
             'actassert': lambda x: assert_validationerror(x.write, {'state_marketing': 'D'}),
             },
            {'arrange': {'state_marketing': 'ES', 'available_qty': MIN_QTY, 'stock_future_qty': 0},
             'actassert': lambda x: assert_validationerror(x.write, {'state_marketing': 'D'}),
             },
            {'arrange': {'state_marketing': 'ES', 'available_qty': MIN_QTY, 'stock_future_qty': MIN_QTY},
             'actassert': lambda x: assert_validationerror(x.write, {'state_marketing': 'D'}),
             },
            {'arrange': {'state_marketing': 'ES', 'available_qty': 0, 'stock_future_qty': MIN_QTY},
             'actassert': lambda x: assert_validationerror(x.write, {'state_marketing': 'H'}),
             },
            {'arrange': {'state_marketing': 'ES', 'available_qty': MIN_QTY, 'stock_future_qty': 0},
             'actassert': lambda x: assert_validationerror(x.write, {'state_marketing': 'H'}),
             },
            {'arrange': {'state_marketing': 'ES', 'available_qty': MIN_QTY, 'stock_future_qty': MIN_QTY},
             'actassert': lambda x: assert_validationerror(x.write, {'state_marketing': 'H'}),
             },

            {'actassert': lambda x: assert_validationerror(
                x.write, {'state_marketing': 'D', 'available_qty': 0, 'stock_future_qty': MIN_QTY}),
             },
            {'actassert': lambda x: assert_validationerror(
                x.write, {'state_marketing': 'D', 'available_qty': MIN_QTY, 'stock_future_qty': 0}),
             },
            {'actassert': lambda x: assert_validationerror(
                x.write, {'state_marketing': 'D', 'available_qty': MIN_QTY, 'stock_future_qty': MIN_QTY}),
             },
            {'actassert': lambda x: assert_validationerror(
                x.write, {'state_marketing': 'H', 'available_qty': 0, 'stock_future_qty': MIN_QTY}),
             },
            {'actassert': lambda x: assert_validationerror(
                x.write, {'state_marketing': 'H', 'available_qty': MIN_QTY, 'stock_future_qty': 0}),
             },
            {'actassert': lambda x: assert_validationerror(
                x.write, {'state_marketing': 'H', 'available_qty': MIN_QTY, 'stock_future_qty': MIN_QTY}),
             },

            {'arrange': {'state_marketing': 'ES', 'available_qty': MIN_QTY, 'stock_future_qty': MIN_QTY},
             'act': lambda x: x.write({'available_qty': 0}),
             'assert': lambda x: self.assertEqual(
                 x.state_marketing, 'ES', "The state marketing has changed and it shouldn't"),
             },
            {'arrange': {'state_marketing': 'ES', 'available_qty': MIN_QTY, 'stock_future_qty': MIN_QTY},
             'act': lambda x: x.write({'stock_future_qty': 0}),
             'assert': lambda x: self.assertEqual(
                 x.state_marketing, 'ES', "The state marketing has changed and it shouldn't"),
             },
            {'arrange': {'state_marketing': 'ES', 'available_qty': MIN_QTY, 'stock_future_qty': MIN_QTY},
             'act': lambda x: x.write({'available_qty': 0, 'stock_future_qty': 0}),
             'assert': lambda x: self.assertEqual(
                 x.state_marketing, 'D',
                 "The state marketing has not changed and it should have changed to discontinued (D)"),
             },

            {'arrange': {'state_marketing': 'ESH', 'available_qty': MIN_QTY, 'stock_future_qty': MIN_QTY},
             'act': lambda x: x.write({'available_qty': MIN_QTY + 1}),
             'assert': lambda x: self.assertEqual(
                 x.state_marketing, 'ESH', "The state marketing has changed and it shouldn't"),
             },
            {'arrange': {'state_marketing': 'ESH', 'available_qty': MIN_QTY, 'stock_future_qty': MIN_QTY},
             'act': lambda x: x.write({'stock_future_qty': MIN_QTY + 1}),
             'assert': lambda x: self.assertEqual(
                 x.state_marketing, 'ESH', "The state marketing has changed and it shouldn't"),
             },
            {'arrange': {'state_marketing': 'ESH', 'available_qty': MIN_QTY, 'stock_future_qty': MIN_QTY},
             'act': lambda x: x.write({'available_qty': 0, 'stock_future_qty': 0}),
             'assert': lambda x: self.assertEqual(
                 x.state_marketing, 'H',
                 "The state marketing has not changed and it should have changed to historical (H)"),
             },

            {'act': lambda x: x.write({'state_marketing': 'D', 'available_qty': 0, 'stock_future_qty': 0}),
             'assert': lambda x: self.assertEqual(
                 x.state_marketing, 'D', "The state marketing has changed and it shouldn't"),
             },
            {'act': lambda x: x.write({'state_marketing': 'H', 'available_qty': 0, 'stock_future_qty': 0}),
             'assert': lambda x: self.assertEqual(
                 x.state_marketing, 'H', "The state marketing has changed and it shouldn't"),
             },

            {'arrange': {'state_marketing': 'C', 'available_qty': MIN_QTY, 'stock_future_qty': MIN_QTY},
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
            {'arrange': {'state_marketing': 'H', 'available_qty': 0, 'stock_future_qty': 0},
             'act': lambda x: x.write({'available_qty': MIN_QTY - 1, 'stock_future_qty': MIN_QTY - 1}),
             'assert': lambda x: self.assertEqual(
                 x.state_marketing, 'ESH',
                 "The state marketing has changed and it shouldn't"),
             },
        ]
        for i, t in enumerate(tests):
            # ARRANGE
            p1 = self.env['lighting.product'].create({
                'reference': 'REF%i' % i,
                'category_id': c1.id,
            })
            if 'arrange' in t:
                p1.write(t['arrange'])
            if 'act' in t:
                t['act'](p1)
            with self.subTest():
                t.get('assert', t.get('actassert'))(p1)
