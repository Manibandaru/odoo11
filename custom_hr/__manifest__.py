
{
    'name': 'HR Custom',
    'version': '1.0',
    'author': 'ManiShankar',
    'category': 'HR',
    'description': """
        This module is customisation of HR playroll
    """,

    'summary': 'This module is customisation of HR playroll',
    'depends': ['base', 'hr', 'hr_payroll'],

    'data': [
            "views/hr_contract_view.xml",
        "views/hr_overtime_view.xml"

    ],

    'installable': True,
    'auto_install': False,
}