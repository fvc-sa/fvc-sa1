from odoo import api, models


class ReportSalesSupplierWise(models.AbstractModel):
    _name = 'report.km_sales_report_by_supplier.sale_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('_get_report_values ===', data['form'])
        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'data': data['form'],
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'company_currency' :data['company_currency'],
        }