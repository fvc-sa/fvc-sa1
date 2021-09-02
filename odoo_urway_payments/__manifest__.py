# -*- coding: utf-8 -*-
{
    'name': "URWAY Payment Gateway",
    'author': "URWAY Technologies",
    'version': '1.0',
    'sequence': 300,
    'license': 'GPL-3',
    'category': 'Accounting/Payment Acquirers',
    'images': ['static/src/img/urway.png'],
    'summary': """
        Allows you to accept mada / VISA / MasterCard via secure payment gateway.""",
    'description': """
        Payment Acquierer built for Odoo 14; URWAY is an emerging payment gateway based in Saudi Arabia. We support mada / VISA / MasterCard
    """,
    'depends': ['payment'],
    'data': [
        'views/urway_acquirer_form.xml',
        'views/urway_templates.xml',
        'data/urway_payment_acquirer.xml',
    ],
    'installable': True,
    'application': True,
    'post_init_hook': 'create_missing_journal_for_acquirers',
    'uninstall_hook': 'uninstall_hook',
}