# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Reports analytics",
    "version": "14.0.1.0.0",
    "author": "RASHAD ALI",
    "summary": "Reports analytics",
    "website": "tel:00967773200611",
    "license": "AGPL-3",
    "depends": ["sale","pos_sale","purchase"],
    "category": "Sales/Sales",
    "data": [
        "security/ir.model.access.csv",
        "views/sale_report_filters.xml",
        "views/purchase_report_filters.xml",
        "views/sale_order_reports_print.xml",
        "views/purchase_order_reports_print.xml",
        "views/assets.xml",
    ],
    'qweb': ['static/src/xml/view.xml'],
    "installable": True,
    "application":True,
}
