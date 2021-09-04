
from odoo import api, fields, models
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
import functools
import time
import logging
_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = "pos.session"

    def _wk_get_utc_time_(self,session_date):
        if session_date:
            try:
                session_date = datetime.strptime(session_date, "%Y-%m-%d %H:%M:%S")
                tz_name = self._context.get('tz') or self.env.user.tz
                tz = tz_name and pytz.timezone(tz_name) or pytz.UTC
                return fields.Datetime.to_string((pytz.UTC.localize(session_date.replace(tzinfo=None), is_dst=False).astimezone(tz).replace(tzinfo=None)))
                
            except ValueError:
                return session_date
    @api.model
    def wk_session_sale_details(self):
        for self_obj in self:
            orders = self_obj.order_ids
            products_sold = {}
            total_sale = 0.0
            order_details = []
            start_date = None
            stop_date = None
            if self_obj.start_at:
                start_date = self_obj.start_at
            if self_obj.stop_at:
                stop_date = self_obj.stop_at
                 
            for order in orders:
                for line in order.lines:

                    key = (line.product_id)
                    products_sold.setdefault(key, 0.0)
                    products_sold[key] += line.qty
                    products_sold[key] += line.product_id.pos_categ_id.id
                    products_sold[key] += line.product_id.pos_categ_id.id

                total_sale += order.amount_total
                wk_order = {
                    'name':order.name,
                    'partner':order.partner_id.name if order.partner_id else '',
                    'date': order.date_order if order.date_order else '',
                    'picking':",".join([picking.name for picking in order.picking_ids]) if len(order.picking_ids.ids) else '',
                    'total_tax':order.amount_tax,
                    'total_amount':order.amount_total,
                    'state':order.state,
                }
                order_details.append(wk_order)
            product_sold_list = sorted(products_sold.items(), key=lambda t: t[1] ,reverse = True)

            return {
                'products': [{
                    'product_id': product.id,
                    'product_name': product.name,
                    'code': product.default_code,
                    'quantity': qty,
                    'uom': product.uom_id.name
                } for (product), qty in product_sold_list],
                'total_sale':total_sale,
                'order_details':order_details,
                'start_date':start_date or '',
                'stop_date':stop_date or ''
            }

    @api.model
    def wk_session_sale_categ_details(self):
        for self_obj in self:
            orders = self_obj.order_ids
            products_sold = {}
            res = {}
            track_category_keys = {}
            array_index = 0
            new_res = []
            total_sale = 0.0
            order_details = []
            start_date = None
            stop_date = None
            if self_obj.start_at:
                start_date = self_obj.start_at
            if self_obj.stop_at:
                stop_date = self_obj.stop_at

            for order in orders:
                for line in order.lines:
                    price_subtotal = 0
                    price_subtotal_incl = 0
                    return_subtotal = 0
                    return_subtotal_incl = 0

                    if line.product_id.pos_categ_id.id not in track_category_keys:
                        if line.price_subtotal < 0 :
                            price_subtotal=0
                            price_subtotal_incl=0
                            return_subtotal =line.price_subtotal
                            return_subtotal_incl = line.price_subtotal_incl
                        else :
                            price_subtotal=line.price_subtotal
                            price_subtotal_incl=line.price_subtotal_incl
                            return_subtotal =0
                            return_subtotal_incl = 0
                        new_res.append({
                            'cat_name': line.product_id.pos_categ_id.name,
                            'cate_total': price_subtotal,
                            'cate_total_incl': price_subtotal_incl,
                            'cate_return_total': return_subtotal,
                            'cate_return_total_incl': return_subtotal_incl,

                            'products': [{
                                'product_name': line.product_id.name,
                                'qty': line.qty,
                                'price_subtotal': price_subtotal,
                                'price_subtotal_incl': price_subtotal_incl,
                                'return_subtotal': return_subtotal,
                                'return_subtotal_incl': return_subtotal_incl,
                             }]
                        })

                        track_category_keys[line.product_id.pos_categ_id.id] = array_index
                        array_index += 1
                    else:
                        which_key = track_category_keys[line.product_id.pos_categ_id.id]
                        if line.price_subtotal < 0 :
                            price_subtotal=0
                            price_subtotal_incl=0
                            return_subtotal =line.price_subtotal
                            return_subtotal_incl = line.price_subtotal_incl
                        else :
                            price_subtotal=line.price_subtotal
                            price_subtotal_incl=line.price_subtotal_incl
                            return_subtotal =0
                            return_subtotal_incl = 0

                        new_res[which_key]['products'].append({
                            'product_name': line.product_id.name,
                            'qty': line.qty,
                            'price_subtotal': price_subtotal,
                            'price_subtotal_incl': price_subtotal_incl,
                            'return_subtotal': return_subtotal,
                            'return_subtotal_incl': return_subtotal_incl,

                        })

                        new_res[which_key]['cate_total'] += price_subtotal
                        new_res[which_key]['cate_total_incl'] += price_subtotal_incl
                        new_res[which_key]['cate_return_total'] += return_subtotal
                        new_res[which_key]['cate_return_total_incl'] += return_subtotal_incl
            _logger.info('wk_session_sale_categ_details %s ', new_res)
            return new_res

    @api.model
    def wk_pos_statement_details(self):
        payment_methods = self.payment_method_ids
        payment_details = []
        for payment_method in payment_methods:
            payment_data = self.env['pos.payment'].search_read([('payment_method_id','=',payment_method.id),('session_id','=',self.id)],['amount'])

            total = [x.get('amount') for x in payment_data]
            data = {
                'name':payment_method.name,
                'amount':sum(total)
            }
            payment_details.append(data)
        return payment_details
        
    @api.model
    def wk_pos_payment_details(self):
        payment_methods = self.payment_method_ids
        payment_details = []
        for payment_method in payment_methods:
            payment_data = self.env['pos.payment'].search_read([('payment_method_id','=',payment_method.id),('session_id','=',self.id)],['payment_date','payment_method_id','pos_order_id','amount'])
            individual_details = {
                                    'id':payment_method.id,
                                    'name':payment_method.name,
                                    'data':payment_data,
                                }
            if len(payment_data) > 0:
                payment_details.append(individual_details)
        return payment_details 


    @api.model
    def get_session_report_data(self, kwargs):
        session = self.browse(kwargs['session_id'])
        report_data = session.wk_session_sale_details() or {}
        report_data['session_info'] = {
            'name':session.name,
            'responsible':session.user_id.name,
            'start_date':session.start_at or '',
            'opening_balance':session.cash_register_balance_start,
            'total_balance':session.cash_register_total_entry_encoding,
        }
        statement_data = []
        for statement in session.statement_ids:
            statement_details = {
                'name':statement.journal_id.name,
                'balance_start': statement.balance_start,
                'total_trans': statement.total_entry_encoding,
                'balance_end': statement.balance_end_real,
                'difference': statement.difference,
            }
            statement_data.append(statement_details)
        report_data['statements'] = statement_data

        return report_data
         



    def wk_print_session_report(self):

        return self.env.ref('pos_session_report_analysis.action_wk_report_pos_session_summary').report_action(self)


    #def wk_send_sesssion_report(self):
    #    context = self._context
    #    template_id = self.env.ref('pos_session_report_analysis.pos_session_report_notify_email',False)
    #    try:
    #        compose_form = self.env.ref('mail.email_compose_message_wizard_form',False)
    #    except ValueError:
    #        compose_form = False
    #    if context==None:
    #        ctx={}
    #    else:
    #        ctx = dict(context)
    #    ctx.update({
    #        'default_model': 'pos.session',
    #        'default_res_id': self.id,
    #        'default_use_template': bool(template_id),
    #        'default_template_id': template_id.id,
    #        })
    #    return {
    #        'name': _('Compose Email'),
    #        'type': 'ir.actions.act_window',
    #        'view_type': 'form',
    #        'view_mode': 'form',
    #        'res_model': 'mail.compose.message',
    #        'views': [(compose_form.id, 'form')],
    #        'view_id': compose_form.id,
    #        'target': 'new',
    #        'context': ctx,
    #    }
