import  ast
from odoo import models, fields, api, _


class PurchaseOrderReportAnalyisWizard(models.TransientModel):
    _name = 'purchasereport.order.wizard'

    start_date = fields.Datetime(string="من تاريخ")
    end_date = fields.Datetime(string="الى تاريخ" )
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.company.id)
    fields_report = fields.Many2many('custom.purchasereport.order',store=False, string='المقاييس')
    fields_hide=fields.Char(string="hide_fields")

    results = fields.Many2many(
        "purchasereport.order",
        string="Results",
        compute="_compute_results",
        help="Use compute fields, so there is nothing stored in database",
    )

    def _compute_results(self):
        """ On the wizard, result will be computed and added to results line
        before export to excel, by using xlsx.export
        """
        self.ensure_one()
        Result = self.env["purchasereport.order"]
        domain = []
        if self.start_date:
            domain += [("date_order", ">=", self.start_date)]
        if self.end_date:
            domain += [("date_order", "<=", self.end_date)]

        domain +=['|',("company_id","=",False),("company_id","=",self.company_id.id)]
        self.results = Result.search(domain)

    def get_selection_label(self, object, field_name, field_value):
        return _(dict(self.env[object].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])

    def print_purchase_report_pdf(self):
        search_dist = []
        data =[]
        fields_hide=[]
        Result = self.env["purchasereport.order"]
        domain = []
        if self.start_date:
            domain += [("date_order", ">=", self.start_date)]
        if self.end_date:
            domain += [("date_order", "<=", self.end_date)]
        domain +=['|',("company_id","=",False),("company_id","=",self.company_id.id)]
        if self.fields_hide:
            for inx in eval(self.fields_hide):
                fields_hide.append(inx)
        search_dist = Result.search(domain)
        final_dist = []
        if search_dist :
            purchase_data = []
            countdata = 0
            for order in search_dist:
                countdata = countdata + 1
                temp_data = []
                temp_data.append(countdata)
                temp_data.append(order.invoice_id)
                temp_data.append(order.order_id)
                temp_data.append(order.vendor)
                temp_data.append(order.date_order)
                temp_data.append(order.quantity)
                temp_data.append(order.amount_untaxed)
                temp_data.append(order.amount_taxed)
                temp_data.append(order.amount_total)
                purchase_data.append(temp_data)
            final_dist = purchase_data


        data = {
            'ids': self,
            'model': 'purchasereport.order.wizard',
            'docs': final_dist,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'fields_hide': fields_hide,
            'company_id':self.company_id.id

        }
        return self.env.ref('reports_analytics.action_report_purchase_pdf').report_action([], data=data)

    def write(self, vals):
        if vals.get('fields_report'):
            fields_hide =vals.get('fields_report')[0][2]
            vals['fields_hide']=fields_hide
        res = super(PurchaseOrderReportAnalyisWizard, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        if vals.get('fields_report'):
            fields_hide =vals.get('fields_report')[0][2]
            vals['fields_hide']=fields_hide


        res = super(PurchaseOrderReportAnalyisWizard, self).create(vals)
        return res

class PurchaseOrderReportAnalyisReportpdf(models.AbstractModel):
    _name = 'report.reports_analytics.purchase_report_pdf'

    @api.model
    def _get_report_values(self, docids, data=None):
        company= self.env["res.company"].search([('id', '=', data['company_id'])])

        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'docs': data['docs'],
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'fields_hide': data['fields_hide'],
            'company_id':company,
        }

