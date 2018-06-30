# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class LightingPortalConnectorSync(models.TransientModel):
    _name = "lighting.portal.connector.sync"

    @api.model
    def synchronize(self, ids=None, context=None, reference=None):
        if not reference:_logger.info('Start syncronization')
        settings = self.env['lighting.portal.connector.settings'].sudo().search([]).sorted(lambda x: x.sequence)
        if settings:
            settings = settings[0]
        else:
            raise UserError(_("No configuration present, please configure database server"))

        from hdbcli import dbapi

        conn = dbapi.connect(settings['host'],
                             settings['port'],
                             settings['username'],
                             settings['password'])

        cursor = conn.cursor()

        # check schema name to void injection on the main query
        stmnt = "SELECT SCHEMA_NAME FROM SCHEMAS"
        cursor.execute(stmnt)
        result = cursor.fetchall()
        if settings['schema'] not in map(lambda x: x[0], result):
            raise ValidationError(_("The schema %s defined in settings does not exists"))

        last_update = fields.datetime.now()

        # execute main query
        stmnt = """SELECT pw."ItemCode" as "reference", p."ItemName" as "description", 
                          c."ItmsGrpNam" as "catalog", 
                          /*pw."OnHand" as "qty_onhand",*/ 
                          pw."OnHand" - pw."IsCommited" + pw."OnOrder" AS "qty_available"
                   FROM %(schema)s.OITW pw, %(schema)s.OITM p, %(schema)s.OITB c
                   WHERE pw."ItemCode" = p."ItemCode" AND
                         (:reference is null OR p."ItemCode" = :reference) AND
                         p."ItmsGrpCod" = c."ItmsGrpCod" AND
                         pw."WhsCode" = '00' AND 
                         p."ItemType" = 'I' AND
                         p."ItmsGrpCod" IN (107, 108, 109, 111) /* Cristher, Dopo, Exo, Indeluz */
                   ORDER BY pw."ItemCode", pw."WhsCode"
                """ % dict(schema=settings['schema'])

        cursor.execute(stmnt, {'reference': reference})
        header = [x[0] for x in cursor.description]
        obj_rs = self.env['lighting.portal.product']
        for row in cursor:
            result0_d = dict(zip(header, row))
            result0_d['qty_available'] = int(result0_d['qty_available'])
            if result0_d['qty_available'] >= 99:
                result0_d['qty_available'] = 99
            elif result0_d['qty_available'] < 0:
                result0_d['qty_available'] = 0

            pim_ref = self.env['lighting.product'].sudo().search([('reference', '=', result0_d['reference'])])
            if pim_ref:
                result0_d['description'] = pim_ref.description
                result0_d['product_id'] = pim_ref.id

            ref_obj = obj_rs.search([('reference', '=', result0_d['reference'])])
            if ref_obj:
                result1_d = {}
                for k0, v0 in result0_d.items():
                    v1 = getattr(ref_obj, k0, None)
                    v1 = v1.id if k0 == 'product_id' else v1
                    if v1 != v0:
                        result1_d[k0] = v0

                result1_d['last_update'] = last_update
                if reference:
                    ref_obj = ref_obj.sudo()
                ref_obj.write(result1_d)
            else:
                result0_d['last_update'] = last_update
                obj_rs.create(result0_d)

        cursor.close()
        conn.close()

        if not reference: _logger.info('End syncronization')

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }