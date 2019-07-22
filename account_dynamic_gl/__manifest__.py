# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Dynamic General Ledger Report',
    'version': '11.0.0.2',
    'category': 'Accounting',
    'author': 'Pycus',
    'summary': 'Dynamic General Ledger Report with interactive drill down view and extra filters',
    'description': """
                This module support for viewing General Ledger (Also Trial Balance mode) on the screen with 
                drilldown option. Also add features to fliter report by Accounts, Account Types 
                and Analytic accounts. Option to download report into Pdf and Xlsx

                    """,
    "price": 45,
    "currency": 'EUR',
    'depends': ['account','report_xlsx'],
    'data': [
             "views/assets.xml",
             "views/views.xml",
    ],
    'demo': [],
    'qweb':['static/src/xml/dynamic_report.xml'],
    "images":['static/description/Dynamic_Gl.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
