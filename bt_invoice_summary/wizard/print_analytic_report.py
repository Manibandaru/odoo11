from odoo import models, fields, api, _
import xlwt
import io
import base64
from xlwt import easyxf
import datetime




class print_analytic_report(models.Model):
    _name = 'print.analytic.report'


    analytic_account = fields.Many2one('account.analytic.account',string='Analytic account')
    date_from = fields.Date(string='From Date')
    date_to=fields.Date(string='To Date')
    file_name = fields.Char('File Name')
    invoice_summary_file = fields.Binary('Invoice Summary Report')
    invoice_report_printed = fields.Boolean('Invoice Report Printed')





    @api.multi
    def action_print_analytic_summary(self):
        workbook = xlwt.Workbook()
        amount_tot = 0
        column_heading_style = easyxf('font:height 200;font:bold True;')
        worksheet = workbook.add_sheet('Analytic Summary')
        worksheet.write(2, 3, self.env.user.company_id.name,
                        easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(4, 2, self.date_from, easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(4, 3, 'To', easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(4, 4, self.date_to, easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(6, 0, _('Analytic Account'), column_heading_style)
        worksheet.write(6, 1, _('Description'), column_heading_style)
        worksheet.write(6, 2, _('Partner'), column_heading_style)
        worksheet.write(6, 3, _('Date'), column_heading_style)
        worksheet.write(6, 4, _('Amount'), column_heading_style)


        worksheet.col(0).width = 5000
        worksheet.col(1).width = 5000
        worksheet.col(2).width = 5000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 5000
        worksheet.col(5).width = 8000



        row = 7
        customer_row = 2
        for wizard in self:
            customer_payment_data = {}
            heading = 'Analytic Summary Report'
            worksheet.write_merge(0, 0, 0, 5, heading, easyxf(
                'font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
            heading = 'Analytic Summary'
            if wizard.analytic_account:
                analytic_objs = self.env['account.analytic.line'].search([('account_id', '=', wizard.analytic_account.id),
                                                                   ])

            for analytic in analytic_objs:
                amount = 0

                worksheet.write(row, 0, analytic.account_id.name)
                worksheet.write(row, 1, analytic.name)
                worksheet.write(row, 2, analytic.partner_id.name)
                worksheet.write(row, 3, analytic.date)
                worksheet.write(row, 4, analytic.amount)
                worksheet.write(row, 5, )
                amount_tot += amount
                row += 1


            fp = io.BytesIO()
            workbook.save(fp)
            excel_file = base64.encodestring(fp.getvalue())
            wizard.invoice_summary_file = excel_file
            wizard.file_name = 'Analytic Summary Report.xls'
            wizard.invoice_report_printed = True
            fp.close()
            return {
                'view_mode': 'form',
                'res_id': wizard.id,
                'res_model': 'print.analytic.report',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'target': 'new',
            }

    @api.multi
    def analytic_summary_pdf(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'analytic_account': self.analytic_account.id,

            },
        }

        return self.env.ref('bt_invoice_summary.analytic_summary_report_id').report_action(self, data=data)



# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:


class ReportAnalyticSummary(models.AbstractModel):
    """Abstract Model for report template.

    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.bt_invoice_summary.report_analytic_summary_id'

    @api.model
    def get_report_values(self, docids, data=None):
        analytic = data['form']['analytic_account']
        print('analytic',analytic,type(analytic))


        docs = []
        analytic_lines = self.env['account.analytic.line'].search([('account_id','=',analytic)])
        print(analytic_lines)
        sum1=0
        for line in analytic_lines:
            sum1 += line.amount
            docs.append({
                'analytic_account': line.account_id.name,
                'description': line.name,
                'partner': line.partner_id.name,
                'date':line.date,
                'amount':line.amount

            })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'sum1':sum1
        }