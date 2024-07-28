# -*- coding: utf-8 -*-
{
    'name': "Quản lý thư viện số",
    'summary': "Quản lý thư viện số",
    'author': "Hà Duy Khánh",
    'website': "https://www.yourcompany.com",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/menu.xml',
        'views/teacher.xml',
        'views/student.xml',
        'views/book.xml',
        'views/computer.xml',
        'views/institute.xml',
        'views/level.xml',
        'views/call_book_card.xml',
        'views/call_computer_card.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}

