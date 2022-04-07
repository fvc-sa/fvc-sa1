
{
    'name': 'Custom Product Labels',
    'version': '14.0.1.0.1',
    'category': 'Sales',
    'author': 'Rashad Alkhawlani',
    'license': 'LGPL-3',
    'depends': [
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/product_label_reports.xml',
        'report/product_label_templates.xml',
        'wizard/print_product_label_views.xml',
    ],

    'application': False,
    'installable': True,
    'auto_install': False,
}
