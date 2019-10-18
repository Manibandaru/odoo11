
{
    'name': 'a2NSoft Essentials',
    'version': '1.0',
    'author': 'Mani Shankar',
    'category': 'Productivity',
    'description': """
        This module helps to do avoid quick creation of the products, customers, vendors, analytical accounts 
    """,

    'summary': 'This module helps to avoid Human Mistakes',
    'depends': ['base', 'sale','account','purchase'],

    'data': [
		'views/custom_sales_order.xml',
	   # "views/purchase_order_report.xml"


    ],

    'installable': True,
    'auto_install': False,
}