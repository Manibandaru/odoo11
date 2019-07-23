# -*- coding: utf-8 -*-
import logging
from odoo import models


class AgedPartnerReportXlsx(models.AbstractModel):
    _name = "report.account_reports_xlsx.aged_partner_report_xls"
    _logger = logging.getLogger(__name__)
    try:
        _inherit = 'report.report_xlsx.abstract'
    except ImportError:
        _logger.debug('Cannot find report_xlsx module for version 11')

    def generate_xlsx_report(self, workbook, obj, vals):
        env_obj = self.env['report.account.report_agedpartnerbalance']
        result_selection = vals.result_selection
        if result_selection == 'customer':
            account_type = ['receivable']
            account_type_name = "Receivable Accounts"
        elif result_selection == 'supplier':
            account_type = ['payable']
            account_type_name = "Payable Accounts"
        else:
            account_type = ['payable', 'receivable']
            account_type_name = "Receivable and Payable Accounts"
        # sales_person_wise = vals.user_wise_report
        date_from = vals.date_from
        target_move = vals.target_move
        if target_move == 'all':
            target_move_name = "All Entries"
        else:
            target_move_name = "All Posted Entries"
        period_length = vals.period_length
        # user_ids = vals.user_ids.ids
        move_lines, total, dummy = env_obj._get_partner_move_lines(account_type, date_from, target_move, period_length)
        sheet = workbook.add_worksheet()
        format1 = workbook.add_format({'font_size': 16, 'align': 'center', 'bg_color': '#D3D3D3', 'bold': True})
        format1.set_font_color('#000080')
        format2 = workbook.add_format({'font_size': 10, 'bold': True})
        format3 = workbook.add_format({'font_size': 10})
        logged_users = self.env['res.company']._company_default_get('account.account')
        sheet.write('A1', logged_users.name, format3)
        sheet.write('A3', 'Start Date:', format2)
        sheet.write('B3', date_from, format3)
        sheet.merge_range('E3:G3', 'Period Length (days):', format2)
        sheet.write('H3', period_length, format3)
        sheet.write('A4', "Partner's:", format2)
        sheet.merge_range('B4:C4', account_type_name, format3)
        sheet.merge_range('E4:F4', 'Target Moves:', format2)
        sheet.merge_range('G4:H4', target_move_name, format3)
        sheet.set_column(0, 0, 20)
        # if sales_person_wise:
        #     sheet.set_column(1, 1, 20)
        #     sheet.merge_range(5, 0, 7, 8, "Aged Partner Balance", format1)
        # else:
        sheet.merge_range(5, 0, 7, 7, "Aged Partner Balance", format1)
        row_value = 8
        column_value = 0
        # if sales_person_wise:
        #     sheet.write(row_value, column_value, "Sales Person", format2)
        #     column_value += 1
        sheet.write(row_value, column_value, "Partners", format2)
        sheet.write(row_value, column_value+1, "Not due", format2)
        sheet.write(row_value, column_value+2, "0-" + str(period_length), format2)
        sheet.write(row_value, column_value+3, str(period_length) + "-" + str(2 * period_length), format2)
        sheet.write(row_value, column_value+4, str(2 * period_length) + "-" + str(3 * period_length), format2)
        sheet.write(row_value, column_value+5, str(3 * period_length) + "-" + str(4 * period_length), format2)
        sheet.write(row_value, column_value+6, "+" + str(4 * period_length), format2)
        sheet.write(row_value, column_value+7, "Total", format2)
        row_value += 1
        column_value = 0
        
        sheet.write(row_value, column_value, "Account Total", format2)
        sheet.write(row_value, column_value + 1, total[6], format2)
        sheet.write(row_value, column_value + 2, total[4], format2)
        sheet.write(row_value, column_value + 3, total[3], format2)
        sheet.write(row_value, column_value + 4, total[2], format2)
        sheet.write(row_value, column_value + 5, total[1], format2)
        sheet.write(row_value, column_value + 6, total[0], format2)
        sheet.write(row_value, column_value + 7, total[5], format2)
        row_value += 1
        for i in move_lines:
            partner_ref = self.env['res.partner'].browse(i['partner_id']).ref
            if partner_ref:
                partner_ref = "[" + str(partner_ref) + "] "
                partner_name = partner_ref + str(i['name'])
            else:
                partner_name = str(i['name'])
            sheet.write(row_value, column_value, partner_name, format3)
            sheet.write(row_value, column_value + 1, i['direction'], format3)
            sheet.write(row_value, column_value + 2, i['4'], format3)
            sheet.write(row_value, column_value + 3, i['3'], format3)
            sheet.write(row_value, column_value + 4, i['2'], format3)
            sheet.write(row_value, column_value + 5, i['1'], format3)
            sheet.write(row_value, column_value + 6, i['0'], format3)
            sheet.write(row_value, column_value + 7, i['total'], format3)
            row_value += 1
