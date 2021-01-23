{
    'name': 'a2NSoft Expense Module',
    'version': '1.0',
    'website' : 'https://www.sidmectech.com',
    'category': 'Account',
    'summary': 'Manage your company  Expenses',
    'description': """
Manage your company Expenses
""",
    'author': 'Mani Shankar',
    'depends': ['account_voucher','base','account','sale','purchase','web'],
    'data': [
        'views/account_payment_view.xml',
            ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}