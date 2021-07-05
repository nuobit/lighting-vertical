# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class LightingProductAdapter(Component):
    _name = 'sapb1.lighting.product.adapter'
    _inherit = 'sapb1.adapter'

    _apply_on = 'sapb1.lighting.product'

    _sql_search = r""""""

    _sql_read = r"""WITH
                    oitm_base AS (
                        SELECT p.*
                        FROM %(schema)s.OITM p
                        WHERE p."U_ACC_Obsmark" IN ('Online', 'Novedades', 'Catalogado', 'Fe Digital', 
                                                    'Descatalogado', 'Fe Histórico','Histórico') and
                              p."ItmsGrpCod" IN (107, 108, 109, 110, 111) -- Cristher, Dopo, Exo, Indeluz, NX Lighting
                    ),
                    -- purchase pricelist
                    purchase_price1 AS (
                        SELECT pl."ItemCode", pl."PriceList", pl."Price", NULLIF(trim(pl."Currency"),'') AS "Currency"
                        FROM %(schema)s.ITM1 pl
                        WHERE pl."PriceList" IN (12, 13) AND
                              pl."Price"!=0 AND NULLIF(trim(pl."Currency"),'') IS NOT NULL
                    ),
                    purchase_price AS (
                        SELECT p."ItemCode", p."Price" AS "PurchasePrice", p."Currency" AS "PurchasePriceCurrency"
                        FROM purchase_price1 p
                        WHERE NOT EXISTS (
                                SELECT p0.*
                                FROM purchase_price1 p0
                                WHERE p0."ItemCode" = p."ItemCode" AND
                                      p0."PriceList" < p."PriceList"
                            )
                    ),
                    -- future stock
                    pending_base AS (
                        SELECT lc."ItemCode",
                               sum(lc."OpenCreQty") AS "OnOrder",
                               lc."ShipDate" AS "ShipDate"
                        FROM %(schema)s.POR1 lc, %(schema)s.OPOR c
                        WHERE lc."DocEntry" = c."DocEntry" AND
                              lc."WhsCode" = '00' AND
                              lc."OpenCreQty" != 0 AND
                              c.CANCELED = 'N'
                        GROUP BY lc."ItemCode", lc."ShipDate"
                        UNION ALL
                        SELECT o."ItemCode",
                               sum(o."PlannedQty" - (o."CmpltQty" + o."RjctQty")) AS "OnOrder",
                               o."DueDate" AS "ShipDate"
                        FROM %(schema)s.OWOR o
                        WHERE o."Warehouse" = '00' AND
                              o."Status" IN ('R', 'P') AND
                              (o."PlannedQty" - (o."CmpltQty" + o."RjctQty")) > 0
                        GROUP BY o."ItemCode", o."DueDate"
                    ),
                    pending_merged AS (
                        SELECT p."ItemCode",
                               sum(p."OnOrder") AS "OnOrder",
                               p."ShipDate" AS "ShipDate"
                        FROM pending_base p
                        GROUP BY p."ItemCode", p."ShipDate"
                    ),
                    stock_future AS (
                        SELECT p."ItemCode",
                               sum(p."OnOrder") AS "OnOrder",
                               max(p."ShipDate") AS "ShipDate"
                        FROM pending_merged p
                        GROUP BY p."ItemCode"
                    ),
                    -- current stock
                    stock_current AS (
                        SELECT pw."ItemCode",
                               pw."OnHand",
                               pw."IsCommited",
                               pw."WhsCode"
                        FROM %(schema)s.OITW pw, %(schema)s.OITM p
                        WHERE pw."ItemCode" = p."ItemCode" AND
                              p."ItemType" = 'I' AND
                              p."InvntItem" = 'Y' AND
                              pw."WhsCode" = '00'
                    ),
                    -- current production orders
                    stock_capacity AS (
                        select lml."Father" AS "ItemCode",
                               min(round((ps."OnHand"- ps."IsCommited") / lml."Quantity",
                                             0, ROUND_DOWN)) AS "Capacity"
                        FROM %(schema)s.ITT1 lml, %(schema)s.OITT c, stock_current ps
                        WHERE lml."Father" = c."Code" AND
                              lml."Code" = ps."ItemCode" AND
                              lml."Warehouse" = ps."WhsCode" AND
                              lml."Quantity" != 0
                        GROUP BY lml."Father"
                    ),
                    -- virtual stock
                    product_virtual_stock AS (
                        SELECT s."ItemCode",
                               0 AS "OnHand",
                               0 AS "IsCommited",
                               s."OnOrder",
                               s."ShipDate",
                               0 AS "Capacity"
                        FROM stock_future s
                        UNION ALL
                        SELECT s."ItemCode",
                               s."OnHand",
                               s."IsCommited",
                               0 AS "OnOrder",
                               NULL AS "ShipDate",
                               0 AS "Capacity"
                        FROM stock_current s
                        UNION ALL
                        SELECT s."ItemCode",
                               0 AS "OnHand",
                               0 AS "IsCommited",
                               0 AS "OnOrder",
                               NULL AS "ShipDate",
                               s."Capacity"
                        FROM stock_capacity s
                    ),
                    product_virtual_stock_all AS (
                        SELECT s."ItemCode",
                               sum(s."OnHand") AS "OnHand",
                               sum(s."IsCommited") AS "IsCommited",
                               sum(s."OnOrder") AS "OnOrder",
                               max(s."ShipDate") AS "ShipDate",
                               sum(s."Capacity") AS "Capacity"
                        FROM product_virtual_stock s
                        GROUP BY s."ItemCode"
                    ),
                    product_data as (
                        SELECT p."ItemCode", p."ItemName",
                               p."CodeBars",
                               g."ItmsGrpCod", g."ItmsGrpNam", p."U_U_familia", p."U_U_aplicacion",
                               p."U_ACC_Obsmark",
                               p."SWeight1", p."SVolume", p."SLength1", p."SWidth1", p."SHeight1",
                               s."OnHand",  s."IsCommited", s."OnOrder", s."ShipDate", s."Capacity",
                               p."AvgPrice", p."LastPurDat",
                               COALESCE(pp."PurchasePrice", 0) AS "PurchasePrice", pp."PurchasePriceCurrency",
                               COALESCE(t."Price", 0) as "Price", NULLIF(trim(t."Currency"),'') AS "Currency"
                        FROM product_virtual_stock_all s,
                             oitm_base p
                                LEFT JOIN %(schema)s.ITM1 t ON t."PriceList" = 11 AND p."ItemCode" = t."ItemCode"
                                LEFT JOIN purchase_price pp ON p."ItemCode" = pp."ItemCode",
                            %(schema)s.OITB g
                        WHERE s."ItemCode" = p."ItemCode" AND
                              p."ItmsGrpCod" = g."ItmsGrpCod"
                    ), product AS (
                        SELECT p.*,
                            bintohex(
                                hash_sha256(
                                    COALESCE(to_binary(p."ItemCode"), '00'), '00',
                                    COALESCE(to_binary(p."ItemName"), '00'), '00',
                                    COALESCE(to_binary(p."CodeBars"), '00'), '00',
                                    COALESCE(to_binary(p."ItmsGrpCod"), '00'), '00',
                                    COALESCE(to_binary(p."U_U_familia"), '00'), '00',
                                    COALESCE(to_binary(p."U_U_aplicacion"), '00'), '00',
                                    COALESCE(to_binary(p."U_ACC_Obsmark"), '00'), '00',
                                    COALESCE(to_binary(p."SWeight1"), '00'), '00',
                                    COALESCE(to_binary(p."SVolume"), '00'), '00',
                                    COALESCE(to_binary(p."SLength1"), '00'), '00',
                                    COALESCE(to_binary(p."SWidth1"), '00'), '00',
                                    COALESCE(to_binary(p."SHeight1"), '00'), '00',
                                    COALESCE(to_binary(p."OnHand"), '00'), '00',
                                    COALESCE(to_binary(p."IsCommited"), '00'), '00',
                                    COALESCE(to_binary(p."OnOrder"), '00'), '00',
                                    COALESCE(to_binary(p."ShipDate"), '00'), '00',
                                    COALESCE(to_binary(p."Capacity"), '00'), '00',
                                    COALESCE(to_binary(p."AvgPrice"), '00'), '00',
                                    COALESCE(to_binary(p."LastPurDat"), '00'), '00',
                                    COALESCE(to_binary(p."PurchasePrice"), '00'), '00',
                                    COALESCE(to_binary(p."PurchasePriceCurrency"), '00'), '00',
                                    COALESCE(to_binary(p."Price"), '00'), '00',
                                    COALESCE(to_binary(p."Currency"), '00'), '00'
                                )
                            ) AS "Hash"
                        FROM product_data p
                    )
                        select %(fields)s
                        from product
                        %(where)s
                     """

    _id = ('ItemCode',)

    _base_table = 'OITM'
    _translatable_fields = ['ItemName', 'U_U_aplicacion']

    def create(self, values_d):
        """ Create a record on the external system """
        raise NotImplementedError("Create products to the Backend is not allowed")

    def search(self, filters=[]):
        """ Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
        _logger.debug(
            '%: method search, sql %s, filters %s',
            self._name, self._sql_read, filters)

        # remove the 'not in' filters
        filters1 = []
        notinops = {}
        for f in filters:
            field, op, values = f
            if op == 'not in':
                notinops[field] = set(values)
            else:
                filters1.append(f)

        res = self.search_read(filters=filters1)

        # apply the 'not in' filter removed before
        res1 = None
        for f, v in notinops.items():
            res_ids = {tuple([x[y] for y in self._id]) for x in res if x[f] not in v}
            if res1 is None:
                res1 = res_ids
            else:
                res1 &= res_ids

        if res1 is not None:
            res = list(res1)
        else:
            res = [tuple([x[f] for f in self._id]) for x in res]

        return res
