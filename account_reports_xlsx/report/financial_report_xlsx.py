# -*- coding: utf-8 -*-
import datetime
import re
import itertools
from odoo import models


class FinancialReportXlsx(models.AbstractModel):
    _name = "report.account_reports_xlsx.financial_report_xls"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        data = {}
        data['form'] = obj.read([])[0]
        comp_dic = {}
        env_obj = obj.env['report.account.report_financial']
        data['form']['used_context'] = {}
        data['form']['used_context']['date_to'] = data['form']['date_to']
        data['form']['used_context']['date_from'] = data['form']['date_from']
        data['form']['used_context']['journal_ids'] = data['form']['journal_ids']
        data['form']['used_context']['state'] = 'posted'
        data['form']['used_context']['strict_range'] = True
        comp_dic['state'] = 'posted'
        comp_dic['journal_ids'] = data['form']['journal_ids']
        data['form']['comparison_context'] = comp_dic
        data['account_report_id'] = data['form']['account_report_id']
        accounting_data = env_obj.get_account_lines(data.get('form'))
        sheet = workbook.add_worksheet()
        format1 = workbook.add_format({'font_size': 16, 'align': 'center', 'bg_color': '#D3D3D3', 'bold': True})
        format1.set_font_color('#000080')
        format1.set_font_name('Times New Roman')
        format2 = workbook.add_format({'font_size': 12, 'bold': True, 'bg_color': '#D3D3D3'})
        format3 = workbook.add_format({'font_size': 10, 'bold': True})
        format4 = workbook.add_format({'font_size': 10})
        format6 = workbook.add_format({'font_size': 10, 'bold': True})
        format7 = workbook.add_format({'font_size': 10})
        format8 = workbook.add_format({'font_size': 12, 'bold': True, 'bg_color': '#D3D3D3'})
        format1.set_align('center')
        format2.set_align('center')
        format3.set_align('center')
        format4.set_align('center')
        format8.set_align('left')
        sheet.set_column('E:E', 10, format4)
        sheet.set_column('H:H', 10, format4)
        sheet.set_column('I:I', 10, format4)
        sheet.set_column('J:J', 10, format4)
        currency = self.env.user.company_id.currency_id.symbol
        format7.set_num_format('0.00 ' + currency)
        format6.set_num_format('0.00 ' + currency)
        report_date = datetime.datetime.now().strftime("%Y-%m-%d")
        sheet.merge_range('A1:B1', "Report Date", format6)
        sheet.merge_range('C1:D1', report_date, format7)
        if obj.account_report_id.name:
            sheet.merge_range(3, 0, 4, 9, obj.account_report_id.name, format1)
        if obj.target_move == 'all':
            target_moves = 'All entries'
        else:
            target_moves = 'All posted entries'
        sheet.merge_range('A7:B7', "Target Moves:", format6)
        sheet.write('C7', target_moves, format7)
        if obj.date_from:
            sheet.write('E7', "Date From:", format6)
            sheet.write('F7', obj.date_from, format7)
        if obj.date_to:
            sheet.write('H7', "Date to:", format6)
            sheet.write('I7', obj.date_to, format7)
        row_number = 9
        col_number = 0
        if obj.debit_credit == 1:
            sheet.merge_range('A9:G9', "Name", format8)
            sheet.write('H9', "Debit", format2)
            sheet.write('I9', "Credit", format2)
            sheet.write('J9', "Balance", format2)
            for values in accounting_data:
                if not self.env.user.company_id.parent_id:
                    if values['level'] != 0:
                        print("l", values)
                else:
                    if values['level'] != 0:
                        print("pp")
                        if values['level'] == 1:
                            sheet.write(row_number, col_number, values['name'], format6)
                            sheet.write(row_number, col_number + 7, values['debit'], format6)
                            sheet.write(row_number, col_number + 8, values['credit'], format6)
                            sheet.write(row_number, col_number + 9, values['balance'], format6)
                            row_number += 1
                        elif not values['account_type'] == 'sum':
                            sheet.write(row_number, col_number, values['name'], format7)
                            sheet.write(row_number, col_number + 7, values['debit'], format7)
                            sheet.write(row_number, col_number + 8, values['credit'], format7)
                            sheet.write(row_number, col_number + 9, values['balance'], format7)
                            row_number += 1

        if not obj.enable_filter and not obj.debit_credit:
            sheet.merge_range('A9:I9', "Name", format8)
            sheet.write('J9', "Balance", format2)
            for values in accounting_data:
                if values['level'] != 0:
                    if values['level'] == 1:
                        # assets and liabilities
                        sheet.write(row_number, col_number, values['name'], format6)
                        sheet.write(row_number, col_number + 9, values['balance'], format6)
                        row_number += 1
                    elif not values['account_type'] == 'sum':
                        sheet.write(row_number, col_number + 1, values['name'], format7)
                        # sheet.write(row_number, col_number, values['name'], format7)
                        sheet.write(row_number, col_number + 9, values['balance'], format7)
                        row_number += 1
        if obj.enable_filter and not obj.debit_credit:
            sheet.merge_range('A9:H9', "Name", format8)
            sheet.write('I9', "Balance", format2)
            sheet.write('J9', data['form']['label_filter'], format2)
            for values in accounting_data:
                if values['level'] != 0:
                    if values['level'] == 1:
                        sheet.write(row_number, col_number, values['name'], format6)
                        sheet.write(row_number, col_number + 8, values['balance'], format6)
                        sheet.write(row_number, col_number + 9, values['balance_cmp'], format6)
                        row_number += 1
                    elif not values['account_type'] == 'sum':
                        sheet.write(row_number, col_number, values['name'], format7)
                        sheet.write(row_number, col_number + 8, values['balance'], format7)
                        sheet.write(row_number, col_number + 9, values['balance_cmp'], format7)
                        row_number += 1


