# -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2013-Today Globalteckz (http://www.globalteckz.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Account Customer statement & Supplier statement & overdue statements',
    'version': '1.0',
    'website' : 'https://www.globalteckz.com',
    'category': 'Base',
    'summary': 'Account Customers statement & Supplier statement & overdue statements',
    'description': """
This module will help you to Print and email Customers & Suppliers with Due Account Statements
customer statement
supplier statement
overdue statement
pending statement
customer follow up
customer overdue statement
customer account statement
supplier account statement
Send customer overdue statements by email
send overdue email
outstanding invoice
customer overdue payments
invoice
reminder
monthly
""",
    'author': 'Globalteckz',
    "price": "49.00",
    "currency": "EUR",
    'images': ['static/description/BANNER.png'],
    "license" : "Other proprietary",
    'depends': ['base','sale','purchase','web'],
    'data': [
        'wizard/account_statements.xml',
        'report/acc_statemnt_view.xml',
        'views/partner_view.xml',
        'views/send_mail_view.xml',
        'report/report_view.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

