#
#
#
# from datetime import datetime
# import time
# from odoo import api, models, _
# from odoo.exceptions import UserError
# from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
#
#
# class ReportPartnerLedger(models.AbstractModel):
#     _name = 'report.bt_invoice_summary.report_analytic_summary_id'
#
#
#     def get_data(self,obj):
#         for wizard in obj:
#             if wizard.analytic_account:
#                 invoice_objs = self.env('account.analytic.line').search([('account_id','=',wizard.analytic_account.id)]).browse()
#         return invoice_objs
#
#     def get_invoice_details(self,line):
#         invoice = self.pool.get('account.analytic.line').browse(line)
#         return invoice
#
#
#     @api.model
#     def get_report_values(self, docids, data=None):
#
#         if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
#             raise UserError(_("Form content is missing, this report cannot be printed."))
#
#         total = []
#         model = self.env.context.get('active_model')
#         docs = self.env[model].browse(self.env.context.get('active_id'))
#
#
#         data=self.get_data(docs)
#         return
#         {
#             'doc_ids': self.ids,
#             'doc_model': model,
#             'data': data['form'],
#             'docs': docs,
#             'time': time,
#             'get_partner_lines': data,
#             # 'get_direction': total,
#         }
#
#
#
#
