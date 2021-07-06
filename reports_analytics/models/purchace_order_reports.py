# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
import logging
from odoo import api, fields, models, tools ,_
from odoo.exceptions import UserError
from odoo.osv.expression import expression

_logger = logging.getLogger(__name__)
class PurchaseOrderReportAnalyis(models.Model):
    _name = "purchasereport.order"
    _description = "Point of Purchace Orders Report"
    _auto = False
    _order = 'date_order desc'
    id = fields.Integer(string="التسلسل", readonly=True,store=True)
    seq = fields.Integer(string="التسلسل", related='id', store=True)
    company_id = fields.Many2one('res.company', string='الشركة',store=True, readonly=True)
    date_order = fields.Datetime(string='التاريخ', readonly=True)
    invoice_id = fields.Char(string="رقم الفاتورة", readonly=True)
    order_id = fields.Char(string="رقم الطلب", readonly=True)
    vendor =  fields.Char(string="شركة التوريد", readonly=True)
    vendor_id=fields.Many2one('res.partner',string='المورد')
    quantity = fields.Float(string='الكمية', readonly=True ,store=True)
    amount_untaxed = fields.Float(string='المبلغ قبل الضريبة', readonly=True ,store=True )
    amount_taxed = fields.Float(string='المبلغ بعد الضريبة', readonly=True ,store=True)
    amount_total = fields.Float(string='الاجمالي', readonly=True , store=True)

    def _select(self):
        select_str = """
                SELECT
                 row_number() over(order by date_order desc) as id,
                 row_number() over(order by date_order desc) as seq,
                 m.name as invoice_id, 
                 o.name as order_id,
                 o.company_id as company_id,
                 p.name as vendor ,
                 p.id as vendor_id,
                 o.date_order as date_order ,
                 (SELECT sum(qty_received) from public.purchase_order_line where order_id =o.id) as quantity ,
                 o.amount_untaxed as amount_untaxed ,
                 o.amount_total as amount_taxed ,
                 o.amount_total as amount_total
        """
        return select_str


    def _from(self):
        return """
            FROM purchase_order AS o 
                INNER JOIN res_partner p ON (p.id = o.partner_id)
                INNER JOIN account_move m ON  (m.invoice_origin = o.name)
            WHERE 
                o.state ='done' and o.invoice_status ='invoiced' and o.company_id = (%s)
        """ % self.env.user.company_id.id

    def _group_by(self):
        group_by_str = """
            GROUP BY
                o.company_id,
                o.user_id,
                o.partner_id,
                o.currency_id,
                l.price_unit,
                o.date_approve,
                l.date_planned,
                l.product_uom,
                o.dest_address_id,
                o.fiscal_position_id,
                l.product_id,
                o.date_order,
                o.state,
                o.id
        """
        return group_by_str


    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
            )
        """ % (self._table, self._select(), self._from())
        )

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=3000, orderby=False, lazy=True):
        """ This is a hack to allow us to correctly calculate the average of PO specific date values since
            the normal report query result will duplicate PO values across its PO lines during joins and
            lead to incorrect aggregation values.

            Only the AVG operator is supported for avg_days_to_purchase.
        """
        ##domain = domain + [('company_id', '=', self.env.company.id)]
        res = []
        if fields:
            res = super(PurchaseOrderReportAnalyis, self).read_group(domain, fields, groupby, offset=offset,
                                                                     limit=limit, orderby=orderby, lazy=lazy)

        return res
