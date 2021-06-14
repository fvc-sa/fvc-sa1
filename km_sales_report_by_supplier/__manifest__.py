{
    'name': 'Sale Order Report By Vendors And Date',
    'version': '14.0.0.0.1',
    'summary': 'Generate your Sale Order reports by Vendor, select multiple Vendors or single Vendor, print report from date and to date',
    'description': """
Generate your Sale Order reports by Vendor, select multiple Vendors or single Vendor, print report from date and to date.
    """,
    'author': 'RASHAD ALI',
    'maintainer': 'RASHAD ALI',
    'category': 'Sales',
    'Company': 'RASHAD ALI',
    'website': 'tel:00967773200611',
    'depends': ['base','sale_management'],
    'license': 'LGPL-3',
    'data':[
        'security/ir.model.access.csv',
        'wizards/sale_report_wizard.xml',
        'reports/sale_reports.xml',
        'reports/sale_report_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 5,
    'application': True,
}
