# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, tools


_logger = logging.getLogger(__name__)
class StockPosOrderReportAnalyis(models.Model):
    _name = "stock.pos.reports"
    _description = "Stock Point of Sale Orders Report"
    _auto = False
    _order = 'id ASC'

    id = fields.Integer(string="التسلسل", readonly=True , store=True)
    seq = fields.Integer(string="التسلسل", related='id' , store=True)
    product_name = fields.Char(string="اسم المنتج", readonly=True)
    product_id = fields.Many2one('product.product',string=" المنتج", readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string="قالب المنتج", readonly=True)
    category = fields.Many2one('product.category' , string="فئة المنتج", readonly=True)
    pos_category = fields.Many2one('pos.category',string="فئة نقطة البيع", readonly=True)
    barcode =  fields.Char(string="الباركود", readonly=True)
    internal_ref = fields.Char(string="المرجع الداخلي", readonly=True)


    discount_amount = fields.Float(  string="مبلغ الخصم" )
    discount_percent = fields.Float( string="نسبة الخصم %")
    qty =fields.Float(string="الكمية")
    amount_untaxed = fields.Float(string='بيع بدون ضريبة')
    amount_taxed = fields.Float(string='بيع مع ضريبة')
    return_qty =fields.Float(string="المرتجع")
    return_total =fields.Float(string="اجمالي المرتجع")


    def _select(self):
        return """
            SELECT
                row_number() over(order by p.id desc) as id,
                row_number() over(order by p.id desc) as seq,
                0 as discount_amount,
                0 as discount_percent,
                0 as qty,
                0 as amount_untaxed ,
                0 as amount_taxed,
                0 as return_qty ,
                0 as return_total,
                t.name AS product_name ,
                p.id as product_id ,
                p.barcode as barcode,
                p.product_tmpl_id as product_tmpl_id,
                p.product_tmpl_id as product_template ,
                p.default_code AS internal_ref,
                c.id as category,
                pc.id as pos_category
         
        """

    def _from(self):
        return """
         FROM public.product_product p 
            inner join public.product_template t on t.id=p.product_tmpl_id
            INNER JOIN product_category c ON (c.id=t.categ_id)
            INNER JOIN pos_category pc ON (pc.id=t.pos_categ_id)
            WHERE 
                t.type='product' and t.active='true' and t.company_id=(%s)
        """ % self.env.user.company_id.id


    def _group_by(self):
        return """
            GROUP BY
                s.id, s.date_order, s.partner_id,s.state, pt.categ_id,
                s.user_id, s.company_id, s.sale_journal,
                s.pricelist_id, s.account_move, s.create_date, s.session_id,
                l.product_id,
                pt.categ_id, pt.pos_categ_id,
                p.product_tmpl_id,
                ps.config_id
        """

    def _having(self):
        return """
            HAVING
                SUM(l.qty * u.factor) != 0
        """

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
        res = []
        if fields:
            res = super(StockPosOrderReportAnalyis, self).read_group(domain, fields, groupby, offset=offset,
                                                                     limit=limit, orderby=orderby, lazy=lazy)

        return res
