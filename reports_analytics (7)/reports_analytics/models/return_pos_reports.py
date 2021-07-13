# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class ReturnPosOrderReportAnalyis(models.Model):
    _name = "return.pos.reports"
    _description = "Return Point of Sale Orders Report"
    _auto = False
    _order = 'date_order desc'

    id = fields.Integer(string="التسلسل", readonly=True, store=True)
    seq = fields.Integer(string="التسلسل", related='id', store=True)
    date_order = fields.Date(string='التاريخ', readonly=True)
    time_order = fields.Char(string='الوقت', readonly=True)
    company_id = fields.Many2one('res.company', store=True, string='الشركة')
    invoice_id = fields.Char(string="رقم الفاتورة", readonly=True)
    product_name = fields.Char(string="اسم المنتج", readonly=True)
    product_template = fields.Many2one('product.template', string=" المنتج", readonly=True)
    product_id = fields.Many2one('product.product', string="المنتج")
    vendor = fields.Many2one('res.partner', string="المزود", readonly=True)
    category = fields.Many2one('product.category', string="فئة المنتج", readonly=True)
    pos_category = fields.Many2one('pos.category', string="فئة نقطة البيع", readonly=True)
    order_id = fields.Char(string="رقم الطلب", readonly=True)
    qty = fields.Float(string='الكمية', readonly=True, store=True)
    session = fields.Char(string="رقم الجلسة", readonly=True)
    user_name = fields.Char(string="المستخدم", readonly=True)
    cashier_name = fields.Char(string="الكاشير", readonly=True)
    barcode = fields.Char(string="الباركود", readonly=True)
    amount_untaxed = fields.Float(string='المبلغ قبل الضريبة', readonly=True, store=True)
    amount_taxed = fields.Float(string='المبلغ بعد الضريبة', readonly=True, store=True)

    def _select(self):
        return """
            SELECT
                row_number() over(order by date_order desc) as id,
                row_number() over(order by date_order desc) as seq,
                l.full_product_name AS product_name ,
                l.product_id as product_id,
                p.product_tmpl_id as product_template ,
                p.barcode AS barcode ,
                c.id as category,
                pc.id as pos_category,
                (SELECT name from Public.product_supplierinfo where product_tmpl_id = p.product_tmpl_id limit 1 ) as vendor,
                l.price_subtotal as amount_untaxed,
                l.price_subtotal_incl as amount_taxed,
                l.qty as qty ,
                date(o.date_order) as date_order,
                cast(cast(o.date_order  as  time) as varchar) as time_order,
                par.name as user_name ,
                o.cashier as cashier_name,
                o.company_id as company_id,
                s.name as session,
                  (SELECT name from account_move where id =o.account_move) as invoice_id, 
                o.name AS order_id
        """

    def _from(self):
        return """
            FROM pos_order_line AS l
                INNER JOIN product_product p ON (p.id=l.product_id)
                INNER JOIN product_template t ON (p.product_tmpl_id=t.id)
                INNER JOIN pos_order o ON (o.id=l.order_id)
                INNER JOIN pos_session s ON (s.id=o.session_id)
                INNER JOIN product_category c ON (c.id=t.categ_id)
                INNER JOIN pos_category pc ON (pc.id=t.pos_categ_id)
                INNER JOIN res_users u ON (u.id=o.user_id)
                INNER JOIN res_partner par ON (par.id=u.partner_id)

            WHERE 
                o.state in ('invoiced','done','paid') and l.qty < 0 
        """

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
            res = super(ReturnPosOrderReportAnalyis, self).read_group(domain, fields, groupby, offset=offset,
                                                                      limit=limit, orderby=orderby, lazy=lazy)

        return res


class ReturnReportCustomFields(models.Model):
    _name = 'custom.return.pos.reports'

    name = fields.Char()
    fields_report = fields.Selection([
        ('seq', 'التسلسل'),
        ('product_name', 'اسم المنتج'),
        ('barcode', 'الباركود'),
        ('category', 'فئة المنتج'),
        ('pos_category', 'فئة نقطة البيع'),
        ('amount_untaxed', 'السعر  بدون الضريبة '),
        ('amount_taxed', 'السعر  بعد الضريبة '),
        ('date_order', 'التاريخ'),
        ('time_order', 'الوقت'),
        ('user_name', 'المستخدم'),
        ('cashier_name', 'الكاشير'),
        ('session', 'رقم الجلسة'),
        ('invoice_id', 'رقم الفاتورة')
    ])

    def name_get(self):
        ''' Here you should define how search the name '''
        res = []
        count = 1
        selectmulti = self.env['custom.return.pos.reports'].fields_get(allfields=['fields_report'])['fields_report'][
            'selection']
        for select in selectmulti:
            res.append((count, select[1], select[0]))
            count += 1

        return res

    def get_selection_by_key(self, key=[]):
        ''' Here you should define how search the name '''
        res = []
        count = 1
        selectmulti = self.env['custom.return.pos.reports'].fields_get(allfields=['fields_report'])['fields_report'][
            'selection']
        for select in selectmulti:

            if count in key:
                res.append(select[0])
            count += 1

        print('get field ===', res)
        return res

    def get_selection_key_by_name(self, key=[]):
        ''' Here you should define how search the name '''
        res = []
        count = 1
        selectmulti = self.env['custom.return.pos.reports'].fields_get(allfields=['fields_report'])['fields_report'][
            'selection']
        for select in selectmulti:

            if select[0] in key:
                res.append(count)
            count += 1

        print('get field ===', res)
        return res


class ReturnOrderReportAnalyisReport(models.AbstractModel):
    _name = 'report_return_pos'
    _description = 'Purchase Order Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['return.pos.reports'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'return.pos.reports',
            'docs': docs,
            'proforma': True
        }