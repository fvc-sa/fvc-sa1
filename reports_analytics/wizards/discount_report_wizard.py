from datetime import datetime, timedelta
from odoo import models, fields, api, _


class DiscountOrderReportAnalyisWizard(models.TransientModel):
    _name = 'discount.pos.order.wizard'
    _check_company_auto = True
    start_date = fields.Datetime(string="من تاريخ" ,default=lambda *a: datetime.strftime(datetime.now()-timedelta(days=31) - timedelta(hours=3) ,'%Y-%m-%d 21:00:00'))
    end_date = fields.Datetime(string="الى تاريخ" ,default=lambda *a: datetime.strftime(datetime.now()-timedelta(hours=3) ,'%Y-%m-%d 20:59:59'))
    category = fields.Many2one('product.category', string="فئة المنتج")
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.company.id)

    pos_category = fields.Many2one('pos.category', string="فئة نقطة البيع")
    vendor = fields.Many2one('res.partner', string="المورد")
    product = fields.Many2one('product.product', string=" المنتج")
    order_id = fields.Char(string="رقم الطلب")
    fields_report = fields.Many2many('custom.discount.pos.reports', store=False, string='اخفاء المقاييس')
    fields_hide = fields.Char(string="hide_fields")
    _defaults = {
        'start_date': lambda *a: datetime.strftime(datetime.now()-timedelta(days=30) ,'%m/%d/%Y 00:00:00'),
        'end_date':  lambda *a: datetime.strftime(datetime.now()+timedelta(days=30) ,'%m/%d/%Y 00:00:00'),
    }
    results = fields.Many2many(
        "discount.pos.reports",
        string="Results",
        compute="_compute_results",
        help="Use compute fields, so there is nothing stored in database",
    )

    def _compute_results(self):
        self.ensure_one()
        Result = self.env["discount.pos.reports"]
        domain = []

        domain += ['|', ("company_id", "=", False), ("company_id", "=", self.company_id.id)]

        if self.start_date:
            domain += [("date_order", ">=", self.start_date)]

        if self.end_date:
            domain += [("date_order", "<=", self.end_date)]
        if self.category:
            domain += [("category", "=", self.category.id)]
        if self.pos_category:
            domain += [("pos_category", "=", self.pos_category.id)]
        # if self.vendor:
        #    domain += [("vendor", "=", self.vendor.id)]
        if self.product:
            domain += [("product_id", "=", self.product.id)]
        if self.order_id:
            domain += [("order_id", "like", self.order_id)]

        if Result.search(domain):
            searchids = []
            for res in Result.search(domain):
                if self.vendor and res.product_tmpl_id and self.get_products_by_vendor(res.product_tmpl_id,
                                                                                       self.vendor):
                    searchids.append(res.id)
                if res.discount_amount > 0:
                    searchids.append(res.id)

            domain += [("id", "in", searchids)]

        self.results = Result.search(domain)

    def get_products_by_vendor(self, product_tmpl_id, vendor_id):
        res = self.env['product.supplierinfo']
        domain = []
        if product_tmpl_id:
            domain += [("product_tmpl_id", "=", product_tmpl_id.id)]
        if vendor_id:
            domain += [("name", "=", vendor_id.id)]

        return res.search(domain)

    def get_selection_label(self, object, field_name, field_value):
        return _(dict(self.env[object].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])

    def print_discount_report_pdf(self):

        fields_hide = []

        search_dist = []
        data = []
        Result = self.env["discount.pos.reports"]
        domain = []
        if self.start_date:
            domain += [("date_order", ">=", self.start_date)]
        if self.end_date:
            domain += [("date_order", "<=", self.end_date)]
        if self.category:
            domain += [("category", "=", self.category.id)]
        if self.pos_category:
            domain += [("pos_category", "=", self.pos_category.id)]
        # if self.vendor:
        #    domain += [("vendor", "=", self.vendor.id)]
        if self.product:
            domain += [("product_id", "=", self.product.id)]
        if self.order_id:
            domain += [("order_id", "like", self.order_id)]
        if self.fields_hide:
            for inx in eval(self.fields_hide):
                fields_hide.append(inx)
        domain += ['|', ("company_id", "=", False), ("company_id", "=", self.company_id.id)]
        search_dist = Result.search(domain)
        final_dist = []
        if search_dist:
            countdata = 0
            purchase_data = []
            for order in search_dist:
                countdata = countdata + 1
                temp_data = []
                temp_data.append(countdata)
                temp_data.append(order.product_name)
                temp_data.append(order.barcode)
                temp_data.append(order.internal_ref)
                temp_data.append(order.category.name)
                temp_data.append(order.pos_category.name)
                temp_data.append(order.qty)
                temp_data.append(order.amount_untaxed)
                temp_data.append(order.amount_taxed)
                temp_data.append(order.discount_percent)
                temp_data.append(order.discount_amount)
                temp_data.append(order.amount_total)
                temp_data.append(order.session)
                temp_data.append(order.invoice_id)
                if self.vendor:
                    if self.get_products_by_vendor(order.product_tmpl_id, self.vendor):
                        purchase_data.append(temp_data)
                elif order.discount_amount > 0:
                    purchase_data.append(temp_data)
            final_dist = purchase_data
        data = {
            'ids': self,
            'model': 'discount.pos.order.wizard',
            'docs': final_dist,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'category': self.category.name,
            'pos_category': self.pos_category.name,
            'vendor': self.vendor.name,
            'product': self.product.name,
            'order_id': self.order_id,
            'fields_hide': fields_hide,
            'company_id': self.company_id.id,

        }
        return self.env.ref('reports_analytics.action_report_discount_pdf').report_action([], data=data)

    def write(self, vals):
        if vals.get('fields_report'):
            fields_hide = vals.get('fields_report')[0][2]
            vals['fields_hide'] = fields_hide
        res = super(DiscountOrderReportAnalyisWizard, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        if vals.get('fields_report'):
            fields_hide = vals.get('fields_report')[0][2]
            vals['fields_hide'] = fields_hide
        res = super(DiscountOrderReportAnalyisWizard, self).create(vals)
        return res


class DiscountOrderReportAnalyisReportpdf(models.AbstractModel):
    _name = 'report.reports_analytics.discount_report_pdf'

    @api.model
    def _get_report_values(self, docids, data=None):
        company = self.env["res.company"].search([('id', '=', data['company_id'])])
        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'docs': data['docs'],
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'category': data['category'],
            'pos_category': data['pos_category'],
            'vendor': data['vendor'],
            'product': data['product'],
            'order_id': data['order_id'],
            'fields_hide': data['fields_hide'],
            'company_id': company,

        }

