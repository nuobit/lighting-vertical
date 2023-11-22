# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from openupgradelib import openupgrade

from odoo import fields

_logger = logging.getLogger(__name__)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return
    _logger.info("Creating Odoo products...")
    category = env.ref("product.product_category_all", raise_if_not_found=False)
    uom = env.ref("product.product_uom_unit", raise_if_not_found=False)
    now = fields.Datetime.now()
    env.cr.execute(
        """  alter table product_template add column x738374_lighting_product_id int4"""
    )
    env.cr.execute(
        """  insert into product_template ("name", default_code, type, categ_id, uom_id, uom_po_id,
                                                      sale_ok, sale_line_warn, active, create_date, write_date,
                                                      x738374_lighting_product_id)
                        select coalesce(coalesce(p.description, p.description_manual), p.reference), p.reference,
                               'consu', %s, %s, %s , true, 'no-message', true, %s, %s, p.id
                        from lighting_product p""",
        (category.id, uom.id, uom.id, now, now),
    )
    env.cr.execute(
        """  insert into product_product (default_code, product_tmpl_id, active, create_date, write_date)
                        select t.default_code, t.id, t.active, t.create_date, t.write_date
                        from product_template t"""
    )
    env.cr.execute(
        """  update lighting_product l
                        set odoo_id = p.id
                        from product_template t, product_product p
                        where t.id = p.product_tmpl_id and
                              t.x738374_lighting_product_id = l.id"""
    )
    env.cr.execute(
        """  alter table product_template drop column x738374_lighting_product_id"""
    )
    _logger.info("Odoo product creation finished!!")
