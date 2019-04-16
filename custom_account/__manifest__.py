
{
    "name": "Custom Accounting Customization",
    "summary": "Odoo 11.0 ",
    "version": "11.0.1.0.23",
    "category": "Accounting",
    "author": 'Mani shankar',
    "description": """
================================================================================

Accounting Customisations 

================================================================================
""",
    'depends': ['base', 'account'],
    'data': ['account_menu_view.xml'

    ],
    'qweb': [

    ],
    'application': True,
    'auto_install': False,
    'installable': True,
    'web_preload': True,

}