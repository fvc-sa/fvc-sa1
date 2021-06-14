from odoo import models, fields, api, _


class SalesReportBySupplier(models.TransientModel):
    _name = 'sale.supplier.report'

    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date", required=True)
    vendor_ids = fields.Many2many('res.partner', 'vendor_report_ids', string="Vendors", required=True)

    def get_selection_label(self, object, field_name, field_value):
        return _(dict(self.env[object].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])

    def print_sale_report_by_supplier(self):
        sales_order = self.env['sale.order'].search([])
        sale_order_groupby_dict = {}
        companycurrency = self.env.ref('base.main_company').currency_id.symbol
        for supplier in self.vendor_ids:
            # filtered_sale_order = list(filter(lambda x: x.user_id == supplier, sales_order))
            filtered_sale_order = list(filter(lambda x: x.partner_id == supplier, sales_order))
            print('filtered_sale_order ===', filtered_sale_order)
            filtered_by_date = list(filter(lambda x: x.date_order >= self.start_date and x.date_order <= self.end_date,
                                           filtered_sale_order))
            print('filtered_by_date ===', filtered_by_date)
            sale_order_groupby_dict[supplier.name] = filtered_by_date

        final_dist = {}
        for supplier in sale_order_groupby_dict.keys():
            sale_data = []
            for order in sale_order_groupby_dict[supplier]:
                temp_data = []
                statename= self.get_selection_label('sale.order', 'state', order.state)
                temp_data.append(order.name)
                temp_data.append(order.date_order)
                temp_data.append(order.user_id.name)
                temp_data.append(statename)
                temp_data.append(order.amount_total)
                temp_data.append(order.currency_id.symbol)
                sale_data.append(temp_data)
            final_dist[supplier] = sale_data
        datas = {
            'ids': self,
            'model': 'sale.supplier.report',
            'form': final_dist,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'company_currency' :companycurrency
        }
        print('last_date ===', final_dist)
        return self.env.ref('km_sales_report_by_supplier.action_report_by_supplier').report_action([], data=datas)
