
{
    'name': 'a2NSoft Vat Report',
    'version': '1.0',
    'author': 'ManiShankar',
    'category': 'Accounting',
    'description': """
        This module is customised VAT Report UAE based clients"
    """,

    'summary': 'This module is customisation of VAT Report',
    'depends': ['base', 'account', ],

    'data': ["report/account_tax_report_uae.xml",
            "views/res_partner_view.xml",
	    "wizard/uae_vat_report_view.xml",
	    "report/report.xml",
             "views/account_move_view.xml"

    ],

    'installable': True,
    'auto_install': False,
}