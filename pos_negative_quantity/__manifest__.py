{
    "name": "Point of Sale - Negative Quantity",
    "version": "14.0.1.0.1",
    "category": "Point Of Sale",
    "summary": "Point of Sale - Negative Quantity",
    "author": "Rashad Ali",
    "website": "tel:00967773200611",
    "license": "AGPL-3",
    "depends": ["point_of_sale","hr","pos_hr"],
    "data": [
        "security/res_groups.xml",
        "views/templates.xml",
        "views/poscongig.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "installable": True,
}
