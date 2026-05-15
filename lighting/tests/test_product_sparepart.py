# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError

from odoo.tests import common
from odoo.tools import mute_logger


class TestProductSparepart(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env["lighting.product.category"].create(
            {"name": "Category 1", "code": "CAT1"}
        )
        cls.product = cls.env["lighting.product"].create(
            {"reference": "REF1", "category_id": cls.category.id}
        )

    def test_create_persists_entries(self):
        self.product.sparepart_ids = [
            (0, 0, {"name": "CRI-1758", "description": "Cristal frontal"}),
            (0, 0, {"name": "COR-1", "description": "Cordón silicona"}),
        ]
        self.assertEqual(len(self.product.sparepart_ids), 2)
        names = self.product.sparepart_ids.mapped("name")
        self.assertIn("CRI-1758", names)
        self.assertIn("COR-1", names)

    def test_sequence_orders_entries(self):
        self.product.sparepart_ids = [
            (0, 0, {"name": "ZZZ-last", "sequence": 20}),
            (0, 0, {"name": "AAA-first", "sequence": 5}),
            (0, 0, {"name": "MMM-mid", "sequence": 10}),
        ]
        ordered = self.product.sparepart_ids.sorted(key=lambda r: (r.sequence, r.id))
        self.assertEqual(ordered.mapped("name"), ["AAA-first", "MMM-mid", "ZZZ-last"])

    def test_unlink_cascades_to_entries(self):
        self.product.sparepart_ids = [(0, 0, {"name": "CRI-1758"})]
        sparepart_id = self.product.sparepart_ids.id
        self.product.unlink()
        self.assertFalse(
            self.env["lighting.product.sparepart"].browse(sparepart_id).exists()
        )

    @mute_logger("odoo.sql_db")
    def test_name_is_required(self):
        with self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                self.env["lighting.product.sparepart"].create(
                    {"product_id": self.product.id}
                )
