# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class LightingPortalConnectorSync(models.TransientModel):
    _name = "lighting.portal.connector.sync"

    @api.model
    def synchronize(self, ids=None, context=None, reference=None):
        if not reference:
            _logger.info("Start syncronization")
        settings = (
            self.env["lighting.portal.connector.settings"]
            .search([])
            .sorted(lambda x: x.sequence)
        )
        if settings:
            settings = settings[0]
        else:
            raise UserError(
                _("No configuration present, please configure database server")
            )

        from hdbcli import dbapi

        conn = dbapi.connect(
            settings["host"],
            settings["port"],
            settings["username"],
            settings["password"],
        )

        cursor = conn.cursor()

        # check schema name to void injection on the main query
        stmnt = "SELECT SCHEMA_NAME FROM SCHEMAS"
        cursor.execute(stmnt)
        result = cursor.fetchall()
        if settings["schema"] not in map(lambda x: x[0], result):
            raise ValidationError(
                _("The schema %s defined in settings does not exists")
            )

        last_update = fields.datetime.now()

        ########## Syncronize Products
        self.synchronize_products(
            cursor, settings["schema"], last_update, reference=reference
        )

        ########## Syncronize ATP
        # self.synchronize_atp(cursor, settings['schema'], last_update, reference=reference)

        cursor.close()
        conn.close()

        if not reference:
            _logger.info("End syncronization")

        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    @api.model
    def synchronize_products(self, cursor, schema, last_update, reference=None):
        stmnt = """WITH product_stock AS (
                        SELECT pw."ItemCode",
                               p."InvntItem",
                               pw."OnHand" - pw."IsCommited" AS "Available"
                        FROM %(schema)s.OITW pw, %(schema)s.OITM p
                        WHERE pw."ItemCode" = p."ItemCode" AND
                              p."ItemType" = 'I' AND
                              pw."WhsCode" = '00'
                    ), product_capacity AS (
                        select lml."Father",
                               min(MAP(ps."InvntItem", 'Y',
                                       round(ps."Available"/lml."Quantity", 0, ROUND_DOWN))) AS "Capacity"
                        from %(schema)s.ITT1 lml, product_stock ps
                        WHERE lml."Code" = ps."ItemCode"
                        GROUP BY lml."Father"
                    ), product_merged AS (
                        SELECT ps."ItemCode", ps."Available", 0 AS "IsKit"
                        FROM product_stock ps
                        UNION ALL
                        SELECT pc."Father" AS "ItemCode",
                               (CASE WHEN pc."Capacity"<0 THEN 0 ELSE pc."Capacity" END)  AS "Available",
                               1 AS "IsKit"
                        FROM product_capacity pc
                    )
                    SELECT pm."ItemCode" as "reference", p."CodeBars" as "barcode",
                           sum(pm."Available") AS "qty_available"
                           /*,(CASE WHEN sum(pm."IsKit") > 0 THEN 'Y' ELSE 'N' END) AS "is_kit"*/
                    FROM product_merged pm, %(schema)s.OITM p
                    WHERE pm."ItemCode" = p."ItemCode" and
                          (:reference is null OR pm."ItemCode" = :reference)
                    GROUP BY pm."ItemCode", p."CodeBars"
                """ % dict(
            schema=schema
        )

        cursor.execute(stmnt, {"reference": reference})
        header = [x[0] for x in cursor.description]
        for row in cursor:
            result0_d = dict(zip(header, row))
            result0_d["qty_available"] = int(result0_d["qty_available"])
            if result0_d["qty_available"] >= 99:
                result0_d["qty_available"] = 99
            elif result0_d["qty_available"] < 0:
                result0_d["qty_available"] = 0

            pim_product = self.env["lighting.product"].search(
                [("reference", "=", result0_d["reference"])]
            )
            if pim_product:
                result0_d["description"] = pim_product.description
                result0_d["product_id"] = pim_product.id

            portal_product = self.env["lighting.portal.product"].search(
                [("reference", "=", result0_d["reference"])]
            )
            if portal_product:
                if not pim_product:
                    portal_product.unlink()
                else:
                    result1_d = {}
                    for k0, v0 in result0_d.items():
                        v1 = getattr(portal_product, k0, None)
                        v1 = v1.id if k0 == "product_id" else v1
                        if v1 != v0:
                            result1_d[k0] = v0

                    result1_d["last_update"] = last_update
                    portal_product.write(result1_d)
            else:
                if pim_product:
                    result0_d["last_update"] = last_update
                    self.env["lighting.portal.product"].create(result0_d)

        # clean residual portal products
        if not reference:
            pim_product_references = (
                self.env["lighting.product"].search([]).mapped("reference")
            )
            portal_product_orphan_ids = self.env["lighting.portal.product"].search(
                [("reference", "not in", pim_product_references)]
            )
            portal_product_orphan_ids.unlink()

    @api.model
    def synchronize_atp(self, cursor, schema, last_update, reference=None):
        stmnt = """WITH atp_onorder AS (
                               SELECT lc."ItemCode",
        	                          lc."OpenCreQty" AS "OnOrder",
        		                      lc."ShipDate"
        	                   FROM %(schema)s.POR1 lc, %(schema)s.OPOR c
        	                   WHERE lc."DocEntry" = c."DocEntry" AND
        	                         (:reference is null OR lc."ItemCode" = :reference) AND
        	                         lc."WhsCode" = '00' AND
        	                         lc."OpenCreQty" != 0 AND
        	                         c.CANCELED = 'N'
        	                   UNION ALL
                               SELECT o."ItemCode",
                                      o."PlannedQty" - (o."CmpltQty" + o."RjctQty") AS "OnOrder",
                                      o."DueDate" AS "ShipDate"
                               FROM %(schema)s.OWOR o
                               WHERE (:reference is null OR o."ItemCode" = :reference) AND
                                     o."Warehouse" = '00' AND
                                     o."Status" IN ('R', 'P') AND
                                     (o."PlannedQty" - (o."CmpltQty" + o."RjctQty")) > 0
                           )
                           SELECT a."ItemCode" AS "reference", a."ShipDate" as "ship_date",
                                  sum(a."OnOrder") AS "qty_ordered"
                           FROM atp_onorder a
                           WHERE DAYS_BETWEEN(CURRENT_DATE, a."ShipDate") <= 7*4
                           GROUP BY a."ItemCode", a."ShipDate"
                           ORDER BY "ItemCode", "ShipDate"
                        """ % dict(
            schema=schema
        )

        cursor.execute(stmnt, {"reference": reference})
        header = [x[0] for x in cursor.description]
        atp_d = {}
        for row in cursor:
            result0_d = dict(zip(header, row))
            result0_d["qty_ordered"] = int(result0_d["qty_ordered"])

            portal_product = self.env["lighting.portal.product"].search(
                [("reference", "=", result0_d["reference"])]
            )
            if portal_product:
                values = {x: result0_d[x] for x in ["ship_date", "qty_ordered"]}
                atp_d.setdefault(portal_product, []).append(values)

        ## updatem
        for product_portal, atp_l in atp_d.items():
            product_portal.atp_ids.unlink()
            product_portal.atp_ids = [(0, False, values) for values in atp_l]
