# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class PosOrderReportAnalyis(models.Model):
    _name = "salereport.pos.order"
    _description = "Point of Sale Orders Report"
    _auto = False
    _order = 'date desc'

    date = fields.Datetime(string='تاريخ الطلب', readonly=True)
    order_id = fields.Many2one('pos.order', string='الطلب', readonly=True)
    partner_id = fields.Many2one('res.partner', string='العميل', readonly=True)
    product_id = fields.Many2one('product.product', string='المنتح', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='قالب المنتح', readonly=True)
    state = fields.Selection(
        [('draft', 'New'), ('paid', 'Paid'), ('done', 'Posted'),
         ('invoiced', 'Invoiced'), ('cancel', 'Cancelled')],
        string='حالة الطلب')
    user_id = fields.Many2one('res.users', string='المستخدم', readonly=True)
    price_total = fields.Float(string='Total Priceا', readonly=True)
    pricewithouttax =fields.Float(string='السعر قبل الضريبة', readonly=True)
    pricewithtax =fields.Float(string='السعر بعد الضريبة', readonly=True)
    price_sub_total = fields.Float(string='السعر قبل الخصم', readonly=True)
    total_discount = fields.Float(string='اجمالي الخصم', readonly=True)

    discount=fields.Float(string='نسبة الخصم', readonly=True)
    average_price = fields.Float(string='السعر المتوسط', readonly=True, group_operator="avg")
    company_id = fields.Many2one('res.company', string='الشركة', readonly=True)
    nbr_lines = fields.Integer(string='عدد المنتجات في الطلب', readonly=True)
    product_qty = fields.Integer(string='الكمية', readonly=True)
    journal_id = fields.Many2one('account.journal', string='الحساب')
    delay_validation = fields.Integer(string='التقييم اليومي')
    product_categ_id = fields.Many2one('product.category', string='الفئة', readonly=True)
    invoiced = fields.Boolean(readonly=True ,string="مفوتر")
    config_id = fields.Many2one('pos.config', string='نقطة البيع', readonly=True)
    pos_categ_id = fields.Many2one('pos.category', string='فئة نقطة البيع', readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', string='قائمة الاسعار', readonly=True)
    session_id = fields.Many2one('pos.session', string='الجلسة', readonly=True)

    def _select(self):
        return """
            SELECT
                MIN(l.id) AS id,
                COUNT(*) AS nbr_lines,
                s.date_order AS date,
                SUM(l.qty) AS product_qty,
                SUM(l.discount) AS discount,
                SUM(l.price_subtotal) AS pricewithouttax,
                SUM(l.price_subtotal_incl) AS pricewithtax,
                SUM(l.qty * l.price_unit / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS price_sub_total,
                SUM(ROUND((l.qty * l.price_unit) * (100 - l.discount) / 100 / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END, cu.decimal_places)) AS price_total,
                SUM((l.qty * l.price_unit) * (l.discount / 100) / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS total_discount,
                (SUM(l.qty*l.price_unit / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END)/SUM(l.qty * u.factor))::decimal AS average_price,
                SUM(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT)) AS delay_validation,
                s.id as order_id,
                s.partner_id AS partner_id,
                s.state AS state,
                s.user_id AS user_id,
                s.company_id AS company_id,
                s.sale_journal AS journal_id,
                l.product_id AS product_id,
                pt.categ_id AS product_categ_id,
                p.product_tmpl_id,
                ps.config_id,
                pt.pos_categ_id,
                s.pricelist_id,
                s.session_id,
                s.account_move IS NOT NULL AS invoiced
        """

    def _from(self):
        return """
            FROM pos_order_line AS l
                INNER JOIN pos_order s ON (s.id=l.order_id)
                LEFT JOIN product_product p ON (l.product_id=p.id)
                LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
                LEFT JOIN uom_uom u ON (u.id=pt.uom_id)
                LEFT JOIN pos_session ps ON (s.session_id=ps.id)
                LEFT JOIN res_company co ON (s.company_id=co.id)
                LEFT JOIN res_currency cu ON (co.currency_id=cu.id)
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
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._group_by(),self._having())
        )
