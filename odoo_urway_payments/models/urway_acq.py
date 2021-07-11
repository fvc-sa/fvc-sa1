# -*- coding: utf-8 -*-
import logging
import requests
import socket

from odoo import models, fields, api
from odoo.exceptions import ValidationError

from werkzeug import urls
from hashlib import sha256

from odoo.addons.odoo_urway_payments.controllers.controllers import UrwayController
from odoo.addons.odoo_urway_payments.controllers.responsecode import URWAY_RESPONSE_CODE

_logger = logging.getLogger(__name__)


class PaymentAcquirerUrway(models.Model):
    """
    Inherits from payment.acquirer
    """
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[
        ('urway', 'Urway')
    ], ondelete={'urway': 'set default'})

    urway_merchant_key = fields.Char(required_if_provider='urway', groups='base.group_user', string="Merchant Key",
                                     help="Enter Merchant Key provided by URWAY team.")
    urway_terminal_id = fields.Char(required_if_provider='urway', groups='base.group_user', string="Terminal ID",
                                    help="Enter Terminal ID provided by URWAY team.")
    urway_password = fields.Char(required_if_provider='urway',
                                 string='Terminal Password', groups='base.group_user',
                                 help="Enter Terminal password provided by URWAY team.")
    urway_request_url = fields.Char(required_if_provider='urway',
                                    string="Request URL", groups='base.group_user',
                                    help="URL to send request to.")

    def urway_form_generate_values(self, tx_values):
        self.ensure_one()
        base_url = self.get_base_url()
        billing_address = {
            "address1": tx_values['billing_partner_address'],
            "postalCode": tx_values['billing_partner_zip'],
            "city": tx_values['billing_partner_city'],
            "countryCode": tx_values['billing_partner_country'].code
        }
        order = {
            "orderType": "ECOM",
            "amount": tx_values['amount'],
            "currencyCode": tx_values['currency'].name,
            "name": tx_values['billing_partner_first_name'] + ' ' + tx_values['billing_partner_last_name'],
            "orderDescription": tx_values['reference'],
            "customerOrderCode": tx_values['reference'],
            "billingAddress": billing_address
        }
        merchantKey = self.sudo().urway_merchant_key
        terminalId = self.sudo().urway_terminal_id
        password = self.sudo().urway_password
        URL = self.sudo().urway_request_url

        orderid = order['customerOrderCode']
        amount = order['amount']
        currency = order['currencyCode']
        country = billing_address['countryCode']
        lang = tx_values["billing_partner_lang"]
        email = tx_values['billing_partner_email']
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)

        txn_details = "" + orderid + "|" + terminalId + "|" + password + "|" + merchantKey + "|" + str(
            amount) + "|" + currency
        hs = sha256(txn_details.encode('utf-8')).hexdigest()

        response_url = urls.url_join(base_url, UrwayController._success_url)

        fields = {
            'trackid': orderid,
            'terminalId': terminalId,
            'customerEmail': email,
            'action': "1",
            'merchantIp': IPAddr,
            'password': password,
            'currency': currency,
            'country': country,
            'amount': amount,
            'udf5': "ODOO",
            'udf3': lang[:2],
            'udf4': "",
            'udf1': "",
            'udf2': response_url,
            'requestHash': hs
        }

        r = requests.post(URL, json=fields)
        if r.status_code == 200:
            urldecode = r.json()
        else:
            raise ValidationError("URWAY cannot communicate with the server. Please contact administrator to resolve the issue.")

        if urldecode['result'] == 'Successful' or urldecode['payid']:
            urway_tx_values = ({
                'tx_id': urldecode['targetUrl'] + "?paymentid=" + urldecode['payid'],
            })
            return urway_tx_values
        else:
            raise ValidationError(
                "ERRCODE %s : %s" % (urldecode['responseCode'], URWAY_RESPONSE_CODE.get(urldecode['responseCode'])))

    def urway_get_form_action_url(self):
        self.ensure_one()
        return self.get_base_url() + UrwayController._process_url


class PaymentTransactionUrway(models.Model):
    _inherit = 'payment.transaction'
    urway_payment_id = fields.Char(string='URWAY Transaction ID', readonly=True)

    @api.model
    def _urway_form_get_tx_from_data(self, data):
        """ Given a data dict coming from urway, verify it and find the related
        transaction record. """
        reference = data.get('TrackId')
        tx = self.search([('reference', '=', reference)])

        if not reference:
            urway_error = data.get('ResponseCode', {})
            _logger.error('URWAY: invalid reply received from URWAY Servers, looks like '
                          'the transaction failed. (error: %s)', urway_error or 'n/a')
            error_msg = "We're sorry to report that the transaction has failed."
            if urway_error:
                error_msg += " " + ("URWAY gave us the following info about the problem: '%s'" %
                                    URWAY_RESPONSE_CODE.get(urway_error))
            error_msg += " " + ("Perhaps the problem can be solved by double-checking your "
                                "credit card details.")
            raise ValidationError(error_msg)

        if not tx:
            error_msg = ('URWAY: no order found for reference %s', reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        elif len(tx) > 1:
            error_msg = ('URWAY: %s orders found for reference %s' % (len(tx), reference))
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        transaction = tx[0]
        acquirer = transaction['acquirer_id']
        merchantKey = acquirer.urway_merchant_key
        terminalId = acquirer.urway_terminal_id
        password = acquirer.urway_password
        URL = acquirer.urway_request_url
        currency = transaction['currency_id'].name
        lang = transaction["partner_lang"]
        email = transaction['partner_email']
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)

        txn_details = "" + reference + "|" + terminalId + "|" + password + "|" + merchantKey + "|" + str(
            data.get('amount')) + "|" + currency
        hs1 = sha256(txn_details.encode('utf-8')).hexdigest()

        fields = {
            'trackid': reference,
            'terminalId': terminalId,
            'customerEmail': email,
            'action': "10",
            'merchantIp': IPAddr,
            'password': password,
            'currency': currency,
            'country': data.get("TranId"),
            'amount': data.get("amount"),
            'udf5': "ODOO",
            'udf3': lang[:2],
            'udf4': "",
            'udf1': "",
            'udf2': "",
            'requestHash': hs1
        }

        r = requests.post(URL, json=fields)
        inquiry = r.json()

        hs2 = sha256((data.get("TranId") + "|" + merchantKey + "|" + data.get("ResponseCode") + "|" + data.get("amount")
                      + "").encode('utf-8')).hexdigest()

        if hs2 != data.get("responseHash") or data.get("Result") != 'Successful':
            if inquiry['result'] != 'Successful' or inquiry['responseCode'] != '000':
                error_msg = (
                        'ERRCODE %s:%s | URWAY: The transcation is invalid %s. Please try again' % (
                    inquiry['responseCode'], URWAY_RESPONSE_CODE.get(inquiry['responseCode']), reference))
                _logger.error(error_msg)
                raise ValidationError(error_msg)
            error_msg = (
                    'ERRCODE %s:%s | URWAY: The transcation response receieved %s might be tempered. Please try again' % (
                data.get("ResponseCode"), URWAY_RESPONSE_CODE.get(data.get("ResponseCode")), reference))
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        return tx[0]

    def _urway_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        return invalid_parameters

    def _urway_form_validate(self, data):
        self.ensure_one()
        if self.state not in ("draft", "pending"):
            _logger.info('URWAY: trying to validate an already validated tx (ref %s)', self.reference)
            return True

        status = data.get('Result')
        tx_id = data.get('TranId')
        vals = {
            "date": fields.datetime.now(),
            "acquirer_reference": tx_id,
            "urway_payment_id" : tx_id
        }
        if status == 'Successful':
            self.write(vals)
            self._set_transaction_done()
            self.execute_callback()
            return True
        else:
            error = data.get("ResponseCode")
            self._set_transaction_error("ERRCODE %s : %s | URWAY: Transaction failed %s" % (
                error, URWAY_RESPONSE_CODE.get(error), data.get('TrackId')))
            return False
