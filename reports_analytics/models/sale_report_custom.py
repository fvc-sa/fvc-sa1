# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    cost = fields.Float(related='product_id.standard_price', store=True, string='Cost')

    #def _select(self):
    #    return super(SaleReport, self)._select() + ",CASE WHEN p.standard_price IS NOT NULL THEN p.standard_price ELSE 0 END as cost"
