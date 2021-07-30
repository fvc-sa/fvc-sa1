# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class DiscountPosOrderReportAnalyis(models.Model):
    _name = "discount.pos.reports"
    _description = "Discount Point of Sale Orders Report"
    _auto = False
    _order = 'date_order desc'

    id = fields.Integer(string="التسلسل", readonly=True, store=True)
    seq = fields.Integer(string="التسلسل", related='id', store=True)
    date_order = fields.Date(string='التاريخ', readonly=True)
    date_order = fields.Char(string='الوقت', readonly=True)
    invoice_id = fields.Char(string="رقم الفاتورة", readonly=True)
    product_name = fields.Char(string="اسم المنتج", readonly=True)
    product_id = fields.Many2one('product.product', string=" المنتج", readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string="قالب المنتج", readonly=True)
    vendor = fields.Many2one('res.partner', string="المورد", readonly=True)
    company_id = fields.Many2one('res.company', store=True, string='Company', readonly=True)
    category = fields.Many2one('product.category', string="فئة المنتج", readonly=True)
    pos_category = fields.Many2one('pos.category', string="فئة نقطة البيع", readonly=True)
    order_id = fields.Char(string="رقم الطلب", readonly=True)
    session = fields.Char(string="رقم الجلسة", readonly=True)
    user_name = fields.Char(string="المستخدم", readonly=True)
    partner_id = fields.Many2one('res.partner', readonly=True, store=True)
    cashier_name = fields.Char(string="الكاشير", readonly=True)
    barcode = fields.Char(string="الباركود", readonly=True)
    qty = fields.Float(string='الكمية المباعة', readonly=True, store=True)
    price_unit = fields.Float(string='السعر', readonly=True, digits=0, store=True)
    internal_ref = fields.Char(string="المرجع الداخلي", readonly=True)
    amount_untaxed = fields.Float(string='المبلغ قبل الضريبة', digits=0, readonly=True, store=True)
    amount_taxed = fields.Float(string='المبلغ بعد الضريبة', digits=0, readonly=True, store=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, states={
        'draft': [('readonly', False)]}, readonly=True)
    discount_amount = fields.Float(compute='_compute_discount_amount', string="مبلغ الخصم", digits=0)
    discount_percent = fields.Float(compute='_compute_discount_percent', string="نسبة الخصم %", digits=0)
    amount_total = fields.Float(string='الاجمالي', readonly=True, store=True)

    @api.depends('pricelist_id', 'product_tmpl_id', 'product_id', 'qty', 'partner_id', 'price_unit')
    def _compute_discount_amount(self):
        suitable_rule = False
        discount_percent = 0
        suitable_rule_id = 0
        for order in self:
            suitable_rule_id = \
            order.pricelist_id.get_product_price_rule(order.product_id, order.qty or 1.0, order.partner_id)[1]
            suitable_rule = self.env['product.pricelist.item'].search([('id', '=', suitable_rule_id)], limit=1)
            # raise ValidationError(_("suitable_rule %(level)s ", level=suitable_rule))
            if suitable_rule and suitable_rule.compute_price == 'fixed' and suitable_rule.base != 'pricelist':
                order.discount_amount = suitable_rule.fixed_price
            elif suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                discount_percent = suitable_rule.percent_price
                if discount_percent > 0:
                    order.discount_amount = ((order.price_unit / (
                                1 - (discount_percent / 100))) - order.price_unit) * order.qty
                else:
                    order.discount_amount = 0
            else:
                order.discount_amount = 0

    @api.depends('pricelist_id', 'product_tmpl_id', 'product_id', 'qty', 'partner_id')
    def _compute_discount_percent(self):
        suitable_rule = False
        suitable_rule_id = 0
        for order in self:
            suitable_rule_id = \
            order.pricelist_id.get_product_price_rule(order.product_id, order.qty or 1.0, order.partner_id)[1]
            suitable_rule = self.env['product.pricelist.item'].search([('id', '=', suitable_rule_id)], limit=1)
            # raise ValidationError(_("suitable_rule %(level)s ", level=suitable_rule))
            if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                order.discount_percent = suitable_rule.percent_price
            else:
                order.discount_percent = 0.00

    def _select(self):
        return """
            SELECT
                row_number() over(order by date_order desc) as id,
                row_number() over(order by date_order desc) as seq,
                l.full_product_name AS product_name ,
                l.qty as qty ,
                0.0 as discount_amount ,
                0.0 as discount_percent ,
                o.partner_id as partner_id ,
                p.barcode AS barcode ,
                o.company_id as company_id ,
                p.default_code AS internal_ref,
                l.product_id AS product_id,
                p.product_tmpl_id as product_tmpl_id,
                (SELECT name from Public.product_supplierinfo where product_tmpl_id = p.product_tmpl_id limit 1 ) as vendor,
                c.id as category,
                pc.id as pos_category,
                o.pricelist_id as pricelist_id,
                l.price_subtotal as amount_untaxed,
                l.price_unit as price_unit ,
                l.price_subtotal_incl as amount_taxed,
                l.price_subtotal_incl as amount_total,
                date(o.date_order) as date_order,
                cast(cast(o.date_order  as  time) as varchar) as time_order,
                par.name as user_name ,
                o.cashier as cashier_name,
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
                o.state  in ('invoiced','done','paid') and  l.qty > 0 and o.pricelist_id > 2
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
            res = super(DiscountPosOrderReportAnalyis, self).read_group(domain, fields, groupby, offset=offset,
                                                                        limit=limit, orderby=orderby, lazy=lazy)

        return res


class DiscountReportCustomFields(models.Model):
    _rec_name = "name"
    _name = 'custom.discount.pos.reports'

    name = fields.Char()
    fields_report = fields.Selection([
        ('seq', 'التسلسل'),
        ('product_name', 'اسم المنتج'),
        ('barcode', 'الباركود'),
        ('internal_ref', 'المرجع'),
        ('category', 'فئة المنتج'),
        ('pos_category', 'فئة نقطة البيع'),
        ('qty', 'الكمية المباعة'),
        ('amount_untaxed', 'سعر البيع بدون الضريبة '),
        ('amount_taxed', 'سعر البيع بعد الضريبة '),
        ('discount_percent', 'نسبة الخصم'),
        ('discount_amount', 'مبلغ الخصم'),
        ('amount_total', 'الاجمالي'),
        ('session', 'رقم الجلسة'),
        ('invoice_id', 'رقم الفاتورة')
    ])

    def name_get(self):
        ''' Here you should define how search the name '''
        res = []
        count = 1
        selectmulti = self.env['custom.discount.pos.reports'].fields_get(allfields=['fields_report'])['fields_report'][
            'selection']
        for select in selectmulti:
            res.append((count, select[1], select[0]))
            count += 1

        return res

    def get_selection_by_key(self, key=[]):
        ''' Here you should define how search the name '''
        res = []
        count = 1
        selectmulti = self.env['custom.discount.pos.reports'].fields_get(allfields=['fields_report'])['fields_report'][
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
        selectmulti = self.env['custom.discount.pos.reports'].fields_get(allfields=['fields_report'])['fields_report'][
            'selection']
        for select in selectmulti:

            if select[0] in key:
                res.append(count)
            count += 1

        print('get field ===', res)
        return res