
{
    'name': 'Product Profit Report',
    'version': '14.0.1.0.0',
    'summary': 'POS Products Profit Report',
    "author": "RASHAD ALI",
    "website": "https://api.whatsapp.com/send?phone=00967773200611",
    'depends': [
        'sale_management', 'point_of_sale','purchase'
    ],
    'data': [
        'wizard/product_profit_report_wizard_view.xml',
        'views/product_profit_report_pdf_report.xml',
        'views/product_profit_report_report.xml',
        'security/ir.model.access.csv',

    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
