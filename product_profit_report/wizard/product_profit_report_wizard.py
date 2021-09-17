# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api


class ProductProfitReport(models.TransientModel):
    _name = "product_profit_report.report"
    _description = 'Product Profit Report'

    @api.model
    def _get_from_date(self):
        company = self.env.user.company_id
        current_date = datetime.date.today()
        from_date = company.compute_fiscalyear_dates(current_date)['date_from']
        return from_date

    from_date = fields.Date(string='من تاريخ', default=_get_from_date, required=True)
    to_date = fields.Date(string='الى تاريخ', default=fields.Date.context_today, required=True)
    company = fields.Many2one('res.company', string='Company', required=True,
                              default=lambda self: self.env.company.id)
    categ_id = fields.Many2one('pos.category', string='الصنف', required=False)
    product_id = fields.Many2one('product.product', string='المنتج', required=False,)
    vendor = fields.Many2one('res.partner', string="المورد")

    @api.onchange('categ_id')
    def _onchange_category_products(self):
        if self.categ_id:
            products = self.env['product.product'].search([('categ_id', '=', self.categ_id.id)])
            return {
                'domain': {'product_id': [('id', 'in', products.ids)]}
            }

    def print_pdf_report(self):
        data = {}
        data['form'] = {
            'ids': self,
            'model': 'product.profit.report.report',
            'from_date': self.from_date,
            'to_date': self.to_date,
            'categ_id': self.categ_id.id,
            'vendore_id':self.vendor.id,
            'product_id': self.product_id.id,
            'company': self.company.id,
        }

        #data['form'].update(self.read([])[0])

        return self.env.ref('product_profit_report.action_product_profit_report_pdf').report_action([], data=data)
