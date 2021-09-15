from datetime import datetime, timedelta
from odoo import models, fields, api, tools, _


class StockOrderReportAnalyisWizard(models.TransientModel):
    _name = 'stock.pos.order.wizard'
    _check_company_auto = True

    start_date = fields.Datetime(string="من تاريخ" ,default=lambda *a: datetime.strftime(datetime.now()-timedelta(days=31) - timedelta(hours=3) ,'%Y-%m-%d 21:00:00'))
    end_date = fields.Datetime(string="الى تاريخ" ,default=lambda *a: datetime.strftime(datetime.now()-timedelta(hours=3) ,'%Y-%m-%d 20:59:59'))
    category = fields.Many2one('product.category', string="فئة المنتج")
    pos_category = fields.Many2one('pos.category', string="فئة نقطة البيع")
    vendor = fields.Many2one('res.partner', string="المورد")
    net_sales_taxed=fields.Float(  string="صافي المبيعات مع الضريبة" ,compute="_compute_results")
    net_sales_untaxed=fields.Float(  string="صافي المبيعات بدون الضريبة" ,compute="_compute_results" )

    product = fields.Many2one('product.product', string=" المنتج")
    order_id = fields.Char(string="رقم الطلب")

    fields_hide = fields.Char(string="hide_fields")

    fields_report = fields.Many2many('custom.stock.pos.reports', store=False, string='اخفاء المقاييس')
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.company.id)
    results = fields.Many2many(
        "stock.pos.reports.temp",
        string="Results",
        check_company=True,
        compute="_compute_results",
        help="Use compute fields, so there is nothing stored in database",
    )

    def compute_return_results(self, product_id=None, vendor_id=None, end_date=None, start_date=None, order_id=None):
        Result = self.env["return.pos.reports"]
        domain = []
        if start_date:
            domain += [("date_order", ">=", start_date)]
        if end_date:
            domain += [("date_order", "<=", end_date)]
        if vendor_id:
            domain += [("vendor", "=", vendor_id.id)]
        if product_id:
            domain += [("product_id", "=", product_id.id)]
        if order_id:
            domain += [("order_id", "like", order_id)]
        domain += ['|', ("company_id", "=", False), ("company_id", "=", self.company_id.id)]

        results = Result.search(domain, limit=1)
        return results

    def compute_discount_amount(self, company_id, product_id=None, end_date=None, start_date=None, order_id=None):
        discount_percent = 0
        suitable_rule_id = 0
        discount_amount = 0
        Result = self.env["pos.order.line"]
        domain = []
        if start_date:
            domain += [("order_id.date_order", ">=", start_date)]
        if end_date:
            domain += [("order_id.date_order", "<=", end_date)]
        if product_id:
            domain += [("product_id", "=", product_id.id)]
        if order_id:
            domain += [("order_id", "=", order_id)]
        domain += [("qty", ">", 0)]
        domain += [("order_id.state", "in", ('invoiced', 'done', 'paid'))]
        domain += ['|', ("company_id", "=", False), ("company_id", "=", company_id.id)]

        results = Result.search(domain)
        for order in results:
            product_id_obj = self.env['product.product'].search([('id', '=', order.product_id.id)], limit=1)
            partner_id_obj = self.env['res.partner'].search([('id', '=', order.order_id.partner_id.id)], limit=1)
            suitable_rule_id = \
            order.order_id.pricelist_id.get_product_price_rule(product_id_obj, order.qty or 1.0, partner_id_obj)[1]
            suitable_rule = self.env['product.pricelist.item'].search([('id', '=', suitable_rule_id)], limit=1)
            # raise validationerror(_("suitable_rule %(level)s ", level=suitable_rule))
            if suitable_rule and suitable_rule.compute_price == 'fixed' and suitable_rule.base != 'pricelist':
                discount_amount = discount_amount + suitable_rule.fixed_price
            elif suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                discount_percent = suitable_rule.percent_price
                if discount_percent > 0:
                    discount_amount = discount_amount + (
                                ((order.price_unit / (1 - (discount_percent / 100))) - order.price_unit) * order.qty)

        return discount_amount

    def compute_discount_percent(self, company_id, product_id=None, end_date=None, start_date=None, order_id=None):
        suitable_rule = False
        suitable_rule_id = 0
        discount_percent = 0
        suitable_rule_id = 0
        discount_amount = 0
        Result = self.env["pos.order.line"]
        domain = []
        if start_date:
            domain += [("order_id.date_order", ">=", start_date)]
        if end_date:
            domain += [("order_id.date_order", "<=", end_date)]
        if product_id:
            domain += [("product_id", "=", product_id.id)]
        if order_id:
            domain += [("order_id", "=", order_id)]
        domain += [("order_id.state", "in", ('invoiced', 'done', 'paid'))]
        domain += ['|', ("company_id", "=", False), ("company_id", "=", company_id.id)]
        domain += [("qty", ">", 0)]
        results = Result.search(domain)
        for order in results:
            product_id_obj = self.env['product.product'].search([('id', '=', order.product_id.id)], limit=1)
            partner_id_obj = self.env['res.partner'].search([('id', '=', order.order_id.partner_id.id)], limit=1)
            suitable_rule_id = \
            order.order_id.pricelist_id.get_product_price_rule(product_id_obj, order.qty or 1.0, partner_id_obj)[1]
            suitable_rule = self.env['product.pricelist.item'].search([('id', '=', suitable_rule_id)], limit=1)
            if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                discount_percent = suitable_rule.percent_price
            else:
                discount_percent = 0.00
            if discount_percent > 0:
                return discount_percent

        return discount_percent

    def compute_purchases(self, product_id=None, end_date=None, start_date=None, order_id=None, vendor_id=None):
        qty_received = 0
        qty_purchase = 0
        amount_taxed = 0
        amount_untaxed = 0
        returnres = {}
        Result = self.env["purchase.order.line"]
        domain = []
        if start_date:
            domain += [("order_id.date_order", ">=", start_date)]
        if end_date:
            domain += [("order_id.date_order", "<=", end_date)]
        if product_id:
            domain += [("product_id", "=", product_id.id)]
        if vendor_id:
            domain += [("order_id.partner_id", "=", vendor_id.id)]
        if order_id:
            domain += [("order_id.name", "like", order_id)]
        domain += [("order_id.state", "in", ('invoiced', 'done', 'paid', 'purchase'))]
        domain += ['|', ("company_id", "=", False), ("company_id", "=", self.company_id.id)]

        results = Result.search(domain)
        for order in results:
            qty_received += order.qty_received
            qty_purchase += order.product_qty
            amount_taxed += order.price_total
            amount_untaxed += order.price_subtotal

        returnres = {
            'qty_received': qty_received,
            'qty_purchase': qty_purchase,
            'amount_taxed': amount_taxed,
            'amount_untaxed': amount_untaxed,
        }
        return returnres

    def compute_sales(self, product_id=None, end_date=None, start_date=None, order_id=None):
        qty_sales = 0
        amount_taxed = 0
        amount_untaxed = 0
        returnres = {}
        Result = self.env["pos.order.line"]
        domain = []
        if start_date:
            domain += [("order_id.date_order", ">=", start_date)]
        if end_date:
            domain += [("order_id.date_order", "<=", end_date)]
        if product_id:
            domain += [("product_id", "=", product_id.id)]
        if order_id:
            domain += [("order_id", "=", order_id)]
        domain += [("order_id.state", "in", ('invoiced', 'done', 'paid'))]
        domain += [("qty", ">", 0)]
        domain += ['|', ("company_id", "=", False), ("company_id", "=", self.company_id.id)]

        results = Result.search(domain)
        for order in results:
            qty_sales += order.qty
            amount_taxed += order.price_subtotal_incl
            amount_untaxed += order.price_subtotal

        returnres = {
            'qty_sales': qty_sales,
            'amount_taxed': amount_taxed,
            'amount_untaxed': amount_untaxed,
        }
        return returnres

    def get_products_by_vendor(self, product_tmpl_id, vendor_id , company_id):
        res = self.env['product.supplierinfo']
        domain = []
        if company_id :
            domain +=[("company_id","=",company_id.id)]
        if product_tmpl_id:
            domain += [("product_tmpl_id", "=", product_tmpl_id.id)]
        if vendor_id:
            domain += [("name", "=", vendor_id.id)]

        return res.search(domain)

    def _compute_results(self):
        """ On the wizard, result will be computed and added to results line
        before export to excel, by using xlsx.export
        """
        # self.ensure_one()
        search_dist = []
        data = []
        sales_taxed=0
        sales_untaxed=0
        return_total=0
        return_sub_total=0
        net_sales_taxed=0
        net_sales_untaxed = 0
        Result = self.env["stock.pos.reports"]
        tmpmodel = self.env["stock.pos.reports.temp"]
        tmpmodel.search([]).unlink()
        domain = []
        # if self.start_date:
        #    domain += [("date_order", ">=", self.start_date)]
        # if self.end_date:
        #    domain += [("date_order", "<=", self.end_date)]
        if self.category:
            domain += [("category", "=", self.category.id)]
        if self.pos_category:
            domain += [("pos_category", "=", self.pos_category.id)]
        # if self.vendor:
        #    domain += [("vendor", "=", self.vendor.id)]
        if self.product:
            domain += [("product_id", "=", self.product.id)]
        # if self.order_id:
        #    domain += [("order_id", "like", self.order_id)]
        # self.results = Result.search(domain)

        domain += ['|', ("company_id", "=", False), ("company_id", "=", self.company_id.id)]
        search_dist = Result.search(domain)

        final_dist = []
        if search_dist:
            purchase_data = []
            counter = 1
            for order in search_dist:

                temp_data = {}

                return_result = {}
                purchase_result = {}
                sales_result = {}
                discount_amount = 0
                discount_percent = 0
                return_result = self.compute_return_results(order.product_id, self.vendor, self.end_date,
                                                            self.start_date, self.order_id)
                purchase_result = self.compute_purchases(order.product_id, self.end_date, self.start_date,
                                                         self.order_id, self.vendor)
                sales_result = self.compute_sales(order.product_id, self.end_date, self.start_date, self.order_id)
                discount_amount = self.compute_discount_amount(self.company_id, order.product_id, self.end_date,
                                                               self.start_date, self.order_id)
                discount_percent = self.compute_discount_percent(self.company_id, order.product_id, self.end_date,
                                                                 self.start_date, self.order_id)
                # order.update({'discount_percent': discount_percent,'discount_amount':discount_amount,'return_qty':return_result.qty,'return_total':return_result.amount_taxed})

                temp_data = {
                    'id': order.id,
                    'seq': counter,
                    'product_name': order.product_id.name,
                    'barcode': order.barcode,
                    'internal_ref': order.internal_ref,
                    'category': order.category.name,
                    'pos_category': order.pos_category.name,
                    'qty_received': purchase_result.get('qty_received'),
                    'qty_purchase': purchase_result.get('qty_purchase'),
                     'qty_available': self.get_product_quantity(order.product_id, self.start_date,self.end_date, self.company_id),
                    #'qty_available': order.product_id.qty_available,
                    'purchase_amount_taxed': purchase_result.get('amount_taxed'),
                    'purchase_amount_untaxed': purchase_result.get('amount_untaxed'),
                    'qty_sales': sales_result.get('qty_sales'),
                    'amount_untaxed': sales_result.get('amount_untaxed'),
                    "amount_taxed": sales_result.get('amount_taxed'),
                    'discount_percent': discount_percent,
                    'discount_amount': discount_amount,
                    'return_qty': return_result.qty,
                    'return_total': return_result.amount_taxed,
                    'return_sub_total': return_result.amount_untaxed,
                    'fields_hide': self.fields_hide,
                }
                if self.vendor:
                    if self.get_products_by_vendor(order.product_tmpl_id, self.vendor,self.company_id):
                        if self.order_id :
                            if purchase_result.get('qty_purchase') > 0 :
                                counter += 1
                                tmpmodel.create(temp_data)
                                sales_untaxed = sales_untaxed + temp_data.get('amount_untaxed')
                                sales_taxed = sales_taxed +  temp_data.get('amount_taxed')
                                return_total = return_total + temp_data.get('return_total')
                                return_sub_total = return_sub_total + temp_data.get('return_sub_total')
                        else :
                            counter += 1
                            tmpmodel.create(temp_data)
                            sales_untaxed = sales_untaxed + temp_data.get('amount_untaxed')
                            sales_taxed = sales_taxed + temp_data.get('amount_taxed')
                            return_total = return_total + temp_data.get('return_total')
                            return_sub_total = return_sub_total + temp_data.get('return_sub_total')

                else:
                    if self.order_id:
                        if purchase_result.get('qty_purchase') > 0:
                            counter += 1
                            tmpmodel.create(temp_data)
                            sales_untaxed = sales_untaxed + temp_data.get('amount_untaxed')
                            sales_taxed = sales_taxed + temp_data.get('amount_taxed')
                            return_total = return_total + temp_data.get('return_total')
                            return_sub_total = return_sub_total + temp_data.get('return_sub_total')
                    else:
                        counter += 1
                        tmpmodel.create(temp_data)
                        sales_untaxed = sales_untaxed + temp_data.get('amount_untaxed')
                        sales_taxed = sales_taxed + temp_data.get('amount_taxed')
                        return_total = return_total + temp_data.get('return_total')
                        return_sub_total = return_sub_total + temp_data.get('return_sub_total')
        self.net_sales_taxed=sales_taxed + return_total
        self.net_sales_untaxed = sales_untaxed + return_sub_total

        self.results = tmpmodel.search([])

    def get_selection_label(self, object, field_name, field_value):
        return _(dict(self.env[object].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])

    def get_product_quantity(self, product_id,start_date,end_date, company_id):
        qty = 0
        res = self.env['stock.quant']
        domain = []
        #domain += [("quantity", ">", 0)]
        if company_id:
            domain += [("company_id", "=", company_id.id)]
        if end_date :
            to_date=end_date
        if product_id:
            domain += [("product_id", "=", product_id.id)]
            warehouseid= self.env['stock.warehouse'].search([("company_id","=",company_id.id)] ,limit=1).id
            if to_date:
                qty = self.env['product.product'].browse(product_id.id).with_context(
                    {'warehouse': warehouseid,'to_date':to_date}).qty_available
            else:
                qty = self.env['product.product'].browse(product_id.id).with_context({'warehouse': warehouseid})
            #qty = res.search(domain, limit=1, order='write_date desc').quantity
            #if qty < 0:
                #qty = 0.00
        return qty

    def print_stock_report_pdf(self):
        search_dist = []
        data = []
        sales_taxed=0
        sales_untaxed=0
        return_total=0
        return_sub_total=0
        net_sales_taxed=0
        net_sales_untaxed = 0
        fields_hide = []
        Result = self.env["stock.pos.reports"]
        domain = []
        # if self.start_date:
        #    domain += [("date_order", ">=", self.start_date)]
        # if self.end_date:
        #    domain += [("date_order", "<=", self.end_date)]
        if self.category:
            domain += [("category", "=", self.category.id)]
        if self.pos_category:
            domain += [("pos_category", "=", self.pos_category.id)]
        # if self.vendor:
        #    domain += [("vendor", "=", self.vendor.id)]
        if self.product:
            domain += [("product_id", "=", self.product.id)]
        if self.fields_hide:
            for inx in eval(self.fields_hide):
                fields_hide.append(inx)
        # if self.order_id:
        #    domain += [("order_id", "like", self.order_id)]
        domain += ['|', ("company_id", "=", False), ("company_id", "=", self.company_id.id)]
        search_dist = Result.search(domain)
        final_dist = []
        if search_dist:
            purchase_data = []
            countdata = 0
            for order in search_dist:
                countdata = countdata + 1
                temp_data = []
                return_result = {}
                purchase_result = {}
                sales_result = {}
                discount_amount = 0
                discount_percent = 0
                product_qty_on_hand=0
                return_result = self.compute_return_results(order.product_id, self.vendor, self.end_date,
                                                            self.start_date, self.order_id)
                purchase_result = self.compute_purchases(order.product_id, self.end_date, self.start_date,
                                                         self.order_id, self.vendor)
                sales_result = self.compute_sales(order.product_id, self.end_date, self.start_date, self.order_id)
                discount_amount = self.compute_discount_amount(self.company_id, order.product_id, self.end_date,
                                                               self.start_date, self.order_id)
                discount_percent = self.compute_discount_percent(self.company_id, order.product_id, self.end_date,
                                                                 self.start_date, self.order_id)
                product_qty_on_hand=self.get_product_quantity(order.product_id,self.start_date,self.end_date,self.company_id)
                temp_data.append(countdata)
                temp_data.append(order.product_id.name)
                temp_data.append(order.barcode)
                temp_data.append(order.internal_ref)
                temp_data.append(order.category.name)
                temp_data.append(order.pos_category.name)
                # temp_data.append(order.qty)
                temp_data.append(purchase_result.get('qty_purchase'))
                temp_data.append(purchase_result.get('qty_received'))
                temp_data.append(product_qty_on_hand)
                # temp_data.append(order.product_tmpl_id.location_id)
                temp_data.append("")
                temp_data.append(purchase_result.get('amount_untaxed'))
                temp_data.append(purchase_result.get('amount_taxed'))
                temp_data.append(sales_result.get('qty_sales'))
                temp_data.append(sales_result.get('amount_untaxed'))
                temp_data.append(sales_result.get('amount_taxed'))
                # temp_data.append(order.amount_untaxed)
                # temp_data.append(order.amount_taxed)
                temp_data.append(discount_percent)
                temp_data.append(discount_amount)
                if return_result:
                    temp_data.append(return_result.qty)
                    temp_data.append(return_result.amount_taxed)
                    temp_data.append(return_result.amount_untaxed)
                else:
                    temp_data.append(0)
                    temp_data.append(0)
                    temp_data.append(0)

                if self.vendor:
                    if self.get_products_by_vendor(order.product_tmpl_id, self.vendor,self.company_id):
                        if self.order_id :
                            if purchase_result.get('qty_purchase') > 0 :
                                purchase_data.append(temp_data)
                                sales_untaxed = sales_untaxed + temp_data[13]
                                sales_taxed = sales_taxed + temp_data[14]
                                return_total = return_total + temp_data[18]
                                return_sub_total = return_sub_total + temp_data[19]
                        else :
                            purchase_data.append(temp_data)
                            sales_untaxed = sales_untaxed + temp_data[13]
                            sales_taxed = sales_taxed + temp_data[14]
                            return_total = return_total + temp_data[18]
                            return_sub_total = return_sub_total + temp_data[19]
                else:
                    if self.order_id:
                        if purchase_result.get('qty_purchase') > 0:
                            purchase_data.append(temp_data)
                            sales_untaxed = sales_untaxed + temp_data[13]
                            sales_taxed = sales_taxed + temp_data[14]
                            return_total = return_total + temp_data[18]
                            return_sub_total = return_sub_total + temp_data[19]
                    else:
                        purchase_data.append(temp_data)
                        sales_untaxed = sales_untaxed + temp_data[13]
                        sales_taxed = sales_taxed +temp_data[14]
                        return_total = return_total + temp_data[18]
                        return_sub_total = return_sub_total + temp_data[19]
                # purchase_data.append(temp_data)
            final_dist = purchase_data

        net_sales_taxed=sales_taxed + return_total
        net_sales_untaxed = sales_untaxed + return_sub_total
        data = {
            'ids': self,
            'model': 'stock.pos.order.wizard',
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
            'net_sales_untaxed':net_sales_untaxed,
            'net_sales_taxed':net_sales_taxed,

        }
        return self.env.ref('reports_analytics.action_report_stock_pdf').report_action([], data=data)

    def export_stock_report_xlsx(self):
        action = {
            'id': 'action_report_stock_excel',
            'type': 'ir.actions.report',
            'name': 'reports_analytics.action_report_stock_excel',
            'report_type': 'excel',
            'report_name': 'stock_report.xlsx',
            'model': 'stock.pos.order.wizard',
            'string': 'تقرير المخزون (.xlsx)',
            'file': 'stock_report',
            'context': dict(self.env.context),

        }
        return action

    def write(self, vals):
        if vals.get('fields_report'):
            fields_hide = vals.get('fields_report')[0][2]
            vals['fields_hide'] = fields_hide
        res = super(StockOrderReportAnalyisWizard, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        if vals.get('fields_report'):
            fields_hide = vals.get('fields_report')[0][2]
            vals['fields_hide'] = fields_hide
        res = super(StockOrderReportAnalyisWizard, self).create(vals)
        return res


class StockTemplateDateForReport(models.Model):
    _name = "stock.pos.reports.temp"
    id = fields.Integer(string="id")
    seq = fields.Integer(string="seq")
    product_name = fields.Char(string="product_name")
    barcode = fields.Char(string="barcode")
    internal_ref = fields.Char(string="internal_ref")
    category = fields.Char(string="category")
    pos_category = fields.Char(string="pos_category")
    qty_received = fields.Float(string="qty_received")
    qty_purchase = fields.Float(string="qty_purchase")
    qty_available = fields.Float(string="qty_available")
    location = fields.Char(string="location", default=" ")
    purchase_amount_taxed = fields.Float(string="purchase_amount_taxed")
    purchase_amount_untaxed = fields.Float(string="purchase_amount_untaxed")
    qty_sales = fields.Float(string="qty_sales")
    amount_untaxed = fields.Float(string="amount_untaxed")
    amount_taxed = fields.Float(string="amount_taxed")
    discount_percent = fields.Float(string="discount_percent")
    discount_amount = fields.Float(string="discount_amount")
    return_qty = fields.Float(string="return_qty")
    return_total = fields.Float(string="return_total")
    return_sub_total=fields.Float(string="return_sub_total")
    fields_hide = fields.Char(string="hide_fields")


class StockOrderReportAnalyisReportpdf(models.AbstractModel):
    _name = 'report.reports_analytics.stock_report_pdf'

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

