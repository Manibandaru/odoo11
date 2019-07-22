# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018 BroadTech IT Solutions Pvt Ltd 
#    (<http://broadtech-innovations.com>).
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
    'name': 'Invoice Summary Report',
    'version': '0.1',
    'category': 'Accounting',
    'summary': 'Invoice Analysis Report',
    'license':'AGPL-3',
    'description': """
    Invoice Summary Report and Analaytic Summary Report
""",
    'author' : 'Mani Shankar',
    'website' : 'http://www.sidmectech.com',
    'depends': ['account_invoicing','partner_ageing_billwise_xlsx'],
    'images': ['static/description/banner.jpg'],
    'data': [
        'wizard/print_invoice_summary_view.xml',
        'wizard/print_analytic_view.xml',
        'report/analytic_summary_report_action.xml',
        'report/analytic_summary_report_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}

# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:
