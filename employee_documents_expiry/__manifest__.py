# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

{
    'name': 'Employee Documents',
    'version': '11.0.1.0.0',
    'summary': """Manages Employee Documents With Expiry Notifications.""",
    'description': """Manages Employee Related Documents with Expiry Notifications.""",
    'category': 'Generic Modules/Human Resources',
    'author': 'Mani Shankar Bandaru',
    'company': 'Sidmec Technologies Pvt Ltd',


    'depends': ['base', 'hr'],
    'data': [
		'security/documents_security_view.xml',
        'security/ir.model.access.csv',

        'views/employee_check_list_view.xml',
        'views/employee_document_view.xml',
	    'views/contact_document_view.xml',
	    'views/document_menu.xml',
    ],


    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
