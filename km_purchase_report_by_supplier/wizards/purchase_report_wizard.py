from odoo import models, fields, api, _


class PurchaseReportBySupplier(models.TransientModel):
    _name = 'purchase.supplier.report'

    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date", required=True)
    vendor_ids = fields.Many2many('res.partner', 'purchase_vendor_report_ids', string="Vendors", required=True)


    def get_selection_label(self, object, field_name, field_value):
        return _(dict(self.env[object].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])

    def print_purchase_report_by_supplier(self):
        purchase_order = self.env['purchase.order'].search([])
        purchase_order_groupby_dict = {}
        companycurrency = self.env.ref('base.main_company').currency_id.symbol
        for supplier in self.vendor_ids:
            # filtered_sale_order = list(filter(lambda x: x.user_id == supplier, sales_order))
            filtered_sale_order = list(filter(lambda x: x.partner_id == supplier, purchase_order))
            print('filtered_sale_order ===', filtered_sale_order)
            filtered_by_date = list(filter(lambda x: x.date_order >= self.start_date and x.date_order <= self.end_date,
                                           filtered_sale_order))
            print('filtered_by_date ===', filtered_by_date)
            purchase_order_groupby_dict[supplier.name] = filtered_by_date

        final_dist = {}
        for supplier in purchase_order_groupby_dict.keys():
            purchase_data = []
            for order in purchase_order_groupby_dict[supplier]:
                temp_data = []
                statename = self.get_selection_label('purchase.order', 'state', order.state)
                temp_data.append(order.name)
                temp_data.append(order.date_order)
                temp_data.append(order.user_id.name)
                temp_data.append(statename)
                temp_data.append(order.amount_total)
                temp_data.append(order.currency_id.symbol)
                purchase_data.append(temp_data)
            final_dist[supplier] = purchase_data
        datas = {
            'ids': self,
            'model': 'purchase.supplier.report',
            'form': final_dist,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'company_currency' :companycurrency
        }
        print('last_date ===', final_dist)
        return self.env.ref('km_purchase_report_by_supplier.action_purchase_report_by_supplier').report_action([], data=datas)
