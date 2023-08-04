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

    def test_color_temperature_flux_000(self):
        """
            is_integrated = False
            is_lamp_included = False
            color_temperature_flux_ids = []
        """
        # ARRANGE & ACT
        t1 = self.env['lighting.product.source.type'].create({
            'code': 'code1',
            'is_integrated': False,
        })

        p1 = self.env['lighting.product'].create({
            'reference': 'reference1',
            'source_ids': [(0, 0, {
                'line_ids': [(0, 0, {
                    'wattage': 100,
                    'is_lamp_included': False,
                    'type_id': t1.id,
                    'color_temperature_flux_ids': [(0, 0, {})],
                })],
            })],
        })

        # ASSERT
        self.assertListEqual(p1.source_ids.line_ids.color_temperature_flux_ids.ids, [],
                             "The color_temperature_flux_ids should be empty")

    def test_color_temperature_flux_001(self):
        """
            is_integrated = False
            is_lamp_included = False
            color_temperature_flux_ids = [Have content]
        """
        # ARRANGE & ACT
        t1 = self.env['lighting.product.source.type'].create({
            'code': 'code1',
            'is_integrated': False,
        })

        p1 = self.env['lighting.product'].create({
            'reference': 'reference1',
            'source_ids': [(0, 0, {
                'line_ids': [(0, 0, {
                    'wattage': 100,
                    'is_lamp_included': False,
                    'type_id': t1.id,
                    'color_temperature_flux_ids': [(0, 0, {
                        'color_temperature_id': self.ref('lighting.product_color_temperature_3000'),
                        'nominal_flux': 1000.11,
                        'flux_magnitude': 'lm'})],
                })],
            })],
        })

        # ASSERT
        self.assertListEqual(p1.source_ids.line_ids.color_temperature_flux_ids.ids, [],
                             "The color_temperature_flux_ids should be empty")

    def test_color_temperature_flux_000_to_011(self):
        """
            is_integrated = False
            is_lamp_included = False -> True
            color_temperature_flux_ids = [] -> [Have content]
        """
        # ARRANGE
        t1 = self.env['lighting.product.source.type'].create({
            'code': 'code1',
            'is_integrated': False,
        })

        p1 = self.env['lighting.product'].create({
            'reference': 'reference1',
            'source_ids': [(0, 0, {
                'line_ids': [(0, 0, {
                    'wattage': 100,
                    'is_lamp_included': False,
                    'type_id': t1.id,
                    'color_temperature_flux_ids': [(0, 0, {})],
                })],
            })],
        })

        # ACT
        p1.source_ids.line_ids.is_lamp_included = True
        p1.source_ids.line_ids.color_temperature_flux_ids = [(0, 0, {
            'color_temperature_id': self.ref('lighting.product_color_temperature_3000'),
            'nominal_flux': 1000.01,
            'flux_magnitude': 'lm'
        })]

        # ASSERT
        self.assertTupleEqual((p1.source_ids.line_ids.color_temperature_flux_ids.color_temperature_id.value,
                               p1.source_ids.line_ids.color_temperature_flux_ids.nominal_flux,
                               p1.source_ids.line_ids.color_temperature_flux_ids.flux_magnitude),
                              (3000, 1000.01, 'lm'),
                              "The color_temperature_flux_ids should be (3000, 1000.01, 'lm')")

    def test_color_temperature_flux_011_to_000(self):
        """
            is_integrated = False
            is_lamp_included = True
            color_temperature_flux_ids = [Have content]
        """
        # ARRANGE
        t1 = self.env['lighting.product.source.type'].create({
            'code': 'code1',
            'is_integrated': False,
        })

        p1 = self.env['lighting.product'].create({
            'reference': 'reference1',
            'source_ids': [(0, 0, {
                'line_ids': [(0, 0, {
                    'wattage': 100,
                    'is_lamp_included': False,
                    'type_id': t1.id,
                    'color_temperature_flux_ids': [(0, 0, {
                        'color_temperature_id': self.ref('lighting.product_color_temperature_3000'),
                        'nominal_flux': 1000.99,
                        'flux_magnitude': 'lm'})],
                })],
            })],
        })

        # ACT
        p1.source_ids.line_ids.is_lamp_included = False

        # ASSERT
        self.assertListEqual(p1.source_ids.line_ids.color_temperature_flux_ids.ids, [],
                             "The color_temperature_flux_ids should be empty")

    def test_color_temperature_flux_101_to_000(self):
        """
            is_integrated = True -> False
            is_lamp_included = False
            color_temperature_flux_ids = [Have content] -> []
        """
        # ARRANGE
        t1 = self.env['lighting.product.source.type'].create({
            'code': 'code1',
            'is_integrated': True,
        })

        p1 = self.env['lighting.product'].create({
            'reference': 'reference1',
            'source_ids': [(0, 0, {
                'line_ids': [(0, 0, {
                    'wattage': 100,
                    'is_lamp_included': False,
                    'type_id': t1.id,
                    'color_temperature_flux_ids': [(0, 0, {
                        'color_temperature_id': self.ref('lighting.product_color_temperature_3000'),
                        'nominal_flux': 1000.77,
                        'flux_magnitude': 'lm'})],
                })],
            })],
        })

        # ACT
        p1.source_ids.line_ids.type_id.is_integrated = False

        # ASSERT
        self.assertListEqual(p1.source_ids.line_ids.color_temperature_flux_ids.ids, [],
                             "The color_temperature_flux_ids should be empty")

    def test_color_temperature_flux_101_to_000_2(self):
        """
            is_integrated = t1.True -> t2.False
            is_lamp_included = False
            color_temperature_flux_ids = [Have content] -> []
        """
        # ARRANGE
        t1 = self.env['lighting.product.source.type'].create({
            'code': 'code1',
            'is_integrated': True,
        })

        t2 = self.env['lighting.product.source.type'].create({
            'code': 'code2',
            'is_integrated': False,
        })

        p1 = self.env['lighting.product'].create({
            'reference': 'reference1',
            'source_ids': [(0, 0, {
                'line_ids': [(0, 0, {
                    'wattage': 100,
                    'is_lamp_included': False,
                    'type_id': t1.id,
                    'color_temperature_flux_ids': [(0, 0, {
                        'color_temperature_id': self.ref('lighting.product_color_temperature_3000'),
                        'nominal_flux': 1000.33,
                        'flux_magnitude': 'lm'})],
                })],
            })],
        })

        # ACT
        p1.source_ids.line_ids.type_id = t2

        # ASSERT
        self.assertListEqual(p1.source_ids.line_ids.color_temperature_flux_ids.ids, [],
                             "The color_temperature_flux_ids should be empty")
