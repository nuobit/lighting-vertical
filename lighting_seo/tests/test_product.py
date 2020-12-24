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

    def test_state_marketing_website_01(self):
        """
        PRE:    - state marketing is discontinued (D) or historical (H)
                - website published is disabled
        ACT:    - enable website published
        POST:   - website published keeps disabled
        """
        # ARRANGE
        c1 = self.env['lighting.product.category'].create({
            'name': 'Category 1',
            'code': 'CAT1'
        })
        p1 = self.env['lighting.product'].create({
            'reference': 'REF1',
            'category_id': c1.id,
            'state_marketing': 'D',
            'website_published': False,
        })
        p2 = self.env['lighting.product'].create({
            'reference': 'REF2',
            'category_id': c1.id,
            'state_marketing': 'H',
            'website_published': False,
        })

        # ACT 1
        p1.website_published = True

        # ASSERT 1
        p1.invalidate_cache(['website_published'], [p1.id])
        with self.subTest():
            self.assertFalse(p1.website_published,
                             "The website published should be kept disabled if state marketing is discontinued (D)")

        # ACT 2
        p2.website_published = True

        # ASSERT 2
        p2.invalidate_cache(['website_published'], [p2.id])
        with self.subTest():
            self.assertFalse(p2.website_published,
                             "The website published should be kept disabled if state marketing is historical (H)")

    def test_state_marketing_website_02(self):
        """
        PRE:    - state marketing is not discontinued (C)
                - website published is enabled
        ACT:    - change state marketing to discontinued (D)
        POST:   - website published is disabled
        """
        # ARRANGE
        c1 = self.env['lighting.product.category'].create({
            'name': 'Category 1',
            'code': 'CAT1'
        })
        p1 = self.env['lighting.product'].create({
            'reference': 'REF1',
            'category_id': c1.id,
            'state_marketing': 'C',
            'website_published': True,
        })

        # ACT
        p1.state_marketing = 'D'

        # ASSERT
        self.assertFalse(p1.website_published, "The website published should be disabled")

    def test_state_marketing_website_03(self):
        """
        PRE:    - state marketing is not discontinued (C)
                - website published is enabled
        ACT:    - change state marketing to discontinued (H)
        POST:   - website published is disabled
        """
        # ARRANGE
        c1 = self.env['lighting.product.category'].create({
            'name': 'Category 1',
            'code': 'CAT1'
        })
        p1 = self.env['lighting.product'].create({
            'reference': 'REF1',
            'category_id': c1.id,
            'state_marketing': 'C',
            'website_published': True,
        })

        # ACT
        p1.state_marketing = 'H'

        # ASSERT
        self.assertFalse(p1.website_published, "The website published should be disabled")

    def test_state_marketing_website_04(self):
        """
        PRE:    - state marketing is not discontinued (C)
                - website published is disabled
        ACT:    - enable website published
        POST:   - website published is still enabled
        """
        # ARRANGE
        c1 = self.env['lighting.product.category'].create({
            'name': 'Category 1',
            'code': 'CAT1'
        })
        p1 = self.env['lighting.product'].create({
            'reference': 'REF1',
            'category_id': c1.id,
            'state_marketing': 'C',
            'website_published': False,
        })

        # ACT
        p1.website_published = True

        # ASSERT
        self.assertTrue(p1.website_published, "The website published should be enabled")

    def test_state_marketing_website_05(self):
        """
        PRE:
        ACT:    - create new product p1
                - p1 has state marketing discontinued (D)
                - website published is enabled
        POST:   - product p1 is created
                - website published is disabled
        """
        # ARRANGE
        c1 = self.env['lighting.product.category'].create({
            'name': 'Category 1',
            'code': 'CAT1'
        })

        # ACT
        p1 = self.env['lighting.product'].create({
            'reference': 'REF1',
            'category_id': c1.id,
            'state_marketing': 'D',
            'website_published': True,
        })

        # ASSERT
        self.assertFalse(p1.website_published, "The website published should be disabled")

    def test_state_marketing_website_06(self):
        """
        PRE:
        ACT:    - create new product p1
                - p1 has state marketing historical (H)
                - website published is enabled
        POST:   - product p1 is created
                - website published is disabled
        """
        # ARRANGE
        c1 = self.env['lighting.product.category'].create({
            'name': 'Category 1',
            'code': 'CAT1'
        })

        # ACT
        p1 = self.env['lighting.product'].create({
            'reference': 'REF1',
            'category_id': c1.id,
            'state_marketing': 'H',
            'website_published': True,
        })

        # ASSERT
        self.assertFalse(p1.website_published, "The website published should be disabled")
