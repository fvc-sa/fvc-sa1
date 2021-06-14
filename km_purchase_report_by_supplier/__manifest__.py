{
    'name': 'Purchase Report By Vendors And Date',
    'version': '14.0.0.0.1',
    'summary': 'Generate your Purchase reports by Vendor, select multiple Vendors or single Vendor, print report from date and to date',
    'description': """
Generate your Purchase reports by Vendor, select multiple Vendors or single Vendor, print report from date and to date.
    """,
    'author': 'RASHAD ALI',
    'maintainer': 'RASHAD ALI',
    'Company': 'RASHAD ALI',
    'website': 'tel:00967773200611',
    'depends': ['base','purchase'],
    'license': 'LGPL-3',
    'data':[
        'security/ir.model.access.csv',
        'wizards/purchase_report_wizard.xml',
        'reports/purchase_reports.xml',
        'reports/purchase_report_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 5,
    'application': True,
}
