import werkzeug

from odoo import http
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
import logging
from odoo.addons.odoo_urway_payments.controllers.responsecode import URWAY_RESPONSE_CODE

_logger = logging.getLogger(__name__)


class UrwayController(http.Controller):
    _success_url = 'payment/urway/success'
    _process_url = 'payment/urway/process'

    @http.route(["/" + _success_url], type='http', auth='public', website=True)
    def urway_success(self, **kwargs):
        _logger.info("URWAY : %s" % kwargs)
        try:
            request.env['payment.transaction'].sudo().form_feedback(kwargs, 'urway')
        except ValidationError as e:
            _logger.info('Unable to validate the URWAY payment')
            values = {
                'urway_err': True,
                'error_code': kwargs['ResponseCode'],
                'message': URWAY_RESPONSE_CODE.get(kwargs['ResponseCode'])
            }
            return request.render("odoo_urway_payments.redirect_fail_page", values)

        return werkzeug.utils.redirect('/payment/process')

    @http.route(["/" + _process_url], type='http', auth='public', csrf=False)
    def urway_process(self, **post):
        postData = post
        if (postData['tx_id'] != False):
            return werkzeug.utils.redirect(postData.get('tx_id'))

