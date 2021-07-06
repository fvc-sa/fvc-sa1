import  ast
from odoo import models, fields, api, _


class DiscountOrderReportAnalyisWizard(models.TransientModel):
    _name = 'discount.pos.order.wizard'

    start_date = fields.Datetime(string="من تاريخ")
    end_date = fields.Datetime(string="الى تاريخ" )
    category = fields.Many2one('product.category' , string="فئة المنتج")
    pos_category = fields.Many2one('pos.category',string="فئة نقطة البيع")
    vendor = fields.Many2one('res.partner', string="المزود")
    product = fields.Many2one('product.product',string=" المنتج")
    order_id = fields.Char(string="رقم الطلب")

    results = fields.Many2many(
        "discount.pos.reports",
        string="Results",
        compute="_compute_results",
        help="Use compute fields, so there is nothing stored in database",
    )

    def _compute_results(self):
        """ On the wizard, result will be computed and added to results line
        before export to excel, by using xlsx.export
        """
        self.ensure_one()
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
        if self.vendor:
            domain += [("vendor", "=", self.vendor.id)]
        if self.product:
            domain += [("product_id", "=", self.product.id)]
        if self.order_id:
            domain += [("order_id", "like", self.order_id)]
        domain +=[("company_id","=",self.env.user.company_id.id)]
        self.results = Result.search(domain)

    def get_selection_label(self, object, field_name, field_value):
        return _(dict(self.env[object].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])

    def print_discount_report_pdf(self):
        search_dist = []
        data =[]
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
        if self.vendor:
            domain += [("vendor", "=", self.vendor.id)]
        if self.product:
            domain += [("product_id", "=", self.product.id)]
        if self.order_id:
            domain += [("order_id", "like", self.order_id)]

        domain +=[("company_id","=",self.env.user.company_id.id)]
        search_dist = Result.search(domain)
        final_dist = []
        if search_dist :
            purchase_data = []
            for order in search_dist:
                temp_data = []
                temp_data.append(order.seq)
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
            'order_id':self.order_id,
        }
        return self.env.ref('reports_analytics.action_report_discount_pdf').report_action([], data=data)


class DiscountOrderReportAnalyisReportpdf(models.AbstractModel):
    _name = 'report.reports_analytics.discount_report_pdf'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('last_date ===',data['docs'])

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
            'order_id':data['order_id'],
        }

