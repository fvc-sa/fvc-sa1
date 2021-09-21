# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Reports analytics",
    "version": "14.0.1.0.0",
    "author": "RASHAD ALI",
    "summary": "Reports analytics",
    "website": "tel:00967773200611",
    "license": "AGPL-3",
    "depends": ["hr","stock","sale","pos_sale","purchase","excel_import_export"],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_report_filters.xml",
        "views/stock_order_reports_print.xml",
        "views/purchase_order_reports_print.xml",
        "views/return_report_filters.xml",
        "views/return_order_reports_print.xml",
        "views/discount_report_filters.xml",
        "views/discount_order_reports_print.xml",
        "views/templates.xml",
        "views/xslxtemplate.xml",
        "wizards/purchase_report_wizard.xml",
        "wizards/discount_report_wizard.xml",
        "wizards/return_report_wizard.xml",
        "wizards/stock_report_wizard.xml"
    ],
    "installable": True,
    "application":True,
}