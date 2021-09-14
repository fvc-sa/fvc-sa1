# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    lock_discount = fields.Boolean(string="Lock discount", default=False)
    discount_password = fields.Char(string="Password")
    admin_discount_rate = fields.Float(string="Discount Rate %")

    @api.constrains('discount_password')
    def check_discount_password(self):
        if self.lock_discount is True:
            for item in str(self.discount_password):
                try:
                    int(item)
                except Exception as e:
                    raise ValidationError(_("The unlock discount password should be a number"))

    @api.constrains('admin_discount_rate')
    def check_discount_rate(self):
        if self.lock_discount is True:
            if self.admin_discount_rate < 1 or self.admin_discount_rate > 99:
                raise ValidationError(_("The  discount rate should be between 1 - 99 "))

