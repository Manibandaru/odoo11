
{
    'name': 'Dynamic Cheque Print',
    'version': '1.0',
    'author': 'ManiShankar',
    'category': 'Account',
    'description': """
        User can print the cheque and also can configure cheque different bank's cheque formats.
    """,

    'summary': 'Dynamic Cheque Print. User can print cheque easily.',
    'depends': ['base', 'sale', 'account', 'account_check_printing'],

    'data': [
		'security/ir.model.access.csv',
         'views/dynamic_cheque_preview.xml',
         'views/dynamic_cheque_format_configuration_view.xml',
         'views/dynamic_cheque_print.xml',
         'views/account_payment_view.xml',
         'views/dynamic_cheque_print_template.xml',
         'dynamic_cheque_print_report.xml',
        # 'data/data_view.xml',
    ],

    'installable': True,
    'auto_install': False,
}