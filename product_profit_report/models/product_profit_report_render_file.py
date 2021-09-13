# -*- coding: utf-8 -*-
import datetime
import logging
from odoo import api, models, _

_logger = logging.getLogger(__name__)


class ReportRender(models.AbstractModel):
    _name = 'report.product_profit_report.report_product_profit_report'
    _description = 'Product profit Report Render'

    def get_product_cost(self, product_id, date_start , date_end ,company_id):
        res = self.env['purchase.order.line']
        domain = []
        result = {}
        if company_id :
            domain +=[("company_id","=",company_id)]
        if product_id:
            domain += [("product_id", "=", product_id.id)]
        #if date_start:
            #domain += [("date_order", ">=", date_start)]
        #if date_end:
            #domain += [("date_order", "<=", date_end)]

        result= res.search(domain,limit=1)
        return result.price_total / result.product_qty

    def get_products_by_vendor(self, vendor_id , company_id):
        res = self.env['product.supplierinfo']
        domain = []
        results={}
        if company_id :
            domain +=[("company_id","=",company_id)]
        if vendor_id:
            domain += [("name", "=", vendor_id)]

        results= res.search(domain)

        return results

    def _get_report_values(self, docids, data=None):
        # only for pdf report
        model_data = data['form']
        return self.generate_report_values(model_data)

        #return self.generate_report_values(model_data)

    @api.model
    def generate_report_values(self, data):
        vendore_products ={}
        categ_id1=''
        product_id1= ''
        vendore_id1= ''
        from_date = data['from_date']
        to_date = data['to_date']
        company = data['company']
        categ_id = data['categ_id']
        product_id = data['product_id']
        vendore_id = data['vendore_id']
        domain = [('order_id.date_order', '>=', from_date),
                  ('order_id.date_order', '<=', to_date),
                  ('company_id', '=', company)]
        if data['categ_id'] :
            domain += [('product_id.categ_id', '=', categ_id)]
            categ_id1 = self.env["pos.category"].search([('id', '=', categ_id)])
        if data['product_id']:
            domain += [('product_id', '=', product_id)]
            product_id1 = self.env["product.product"].search([('id', '=', product_id)])

        if data['vendore_id'] :

            domain += [('product_id.product_tmpl_id.seller_ids.name', '=', vendore_id)]
            vendore_id1 = self.env["res.partner"].search([('id', '=', vendore_id)])

        orders = self.env['pos.order.line'].search(domain, order='name')

        groups = {}

        for order in orders:
            return_qty = 0
            return_price = 0
            dic_name = str(order.product_id.id)
            quantity = order.qty
            #price = quantity * (order.price_unit - order.discount)
            price = order.price_subtotal_incl
            expense= self.get_product_cost(order.product_id,order.order_id.date_order,order.order_id.date_order,company) * quantity
            #expense = order.product_id.get_history_price(order.company_id.id, date=order.order_id.date_order) * quantity
            if not expense or expense == 0.0:
                expense = order.product_id.standard_price * quantity
            if order.qty <  0 :
                return_qty = order.qty
                return_price = price

                #quantity = quantity
                #price = price
                #expense = expense


            profit = price - expense
            if not groups.get(dic_name):
                groups[dic_name] = {}
                groups[dic_name].update({
                    'qty': quantity,
                    'unit': order.product_id.uom_id.name,
                    'sales': price,
                    'categ':order.product_id.categ_id.name,
                    'expense': expense,
                    'profit': profit,
                    'return_qty':return_qty,
                    'return':return_price,
                    'barcode':order.product_id.barcode,
                    'name': order.product_id.name
                })
            else:
                groups[dic_name].update({
                    'qty': groups[dic_name].get('qty') + quantity,
                    'sales': groups[dic_name].get('sales') + price,
                    'expense': groups[dic_name].get('expense') + expense,
                    'profit': groups[dic_name].get('profit') + profit,
                    'return_qty': groups[dic_name].get('return_qty') + return_qty,
                    'return': groups[dic_name].get('return') + return_price

                })
        company_id = self.env["res.company"].search([('id', '=', data['company'])])


        return {
            'data': data,
            'groups': groups,
            'company':company_id,
            'categ_id':categ_id1,
            'product_id':product_id1,
            'vendore_id':vendore_id1,

            'report_date': datetime.datetime.now().strftime("%Y-%m-%d"),
        }
