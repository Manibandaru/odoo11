# -*- coding: utf-8 -*-
import datetime
import logging
from odoo import models


class GeneralLedgerReportXlsx(models.Model):
    _name = "report.account_reports_xlsx.ledger_report_xls"
    _logger = logging.getLogger(__name__)
    try:
        _inherit = 'report.report_xlsx.abstract'
    except ImportError:
        _logger.debug('Cannot find report_xlsx module for version 11')

    def generate_xlsx_report(self, workbook, obj, vals):
        data = {}
        data['form'] = vals.read([])[0]
        data['model'] = 'ir.ui.menu'
        data['ids'] = []
        data['form']['used_context'] = {
            'date_to': vals.date_to,
            'date_from': vals.date_from,
            'strict_range': True,
            'state': vals.target_move,
            'active_model': 'account.account' if vals.active_account else None,
            'active_ids': [vals.active_account.id] if vals.active_account else None,
            'active_id': vals.active_account.id if vals.active_account else None,
            'journal_ids': vals.journal_ids.ids,
        }

        env_obj = vals.env['report.account.report_generalledger']
        sortby = data['form'].get('sortby', 'sort_date')
        display_account = data['form']['display_account']
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in
                     self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]
        accounts = vals.active_account if vals.active_account else self.env['account.account'].search([])
        init_balance = vals['initial_balance']
        report_obj = env_obj.with_context(data['form'].get('used_context', {}))._get_account_move_entry(
                                                            accounts, init_balance, sortby, display_account)
        sheet = workbook.add_worksheet()
        format1 = workbook.add_format({'font_size': 16, 'align': 'center', 'bg_color': '#D3D3D3', 'bold': True})
        format1.set_font_color('#000080')
        format2 = workbook.add_format({'font_size': 12, 'bold': True, 'bg_color': '#D3D3D3'})
        format3 = workbook.add_format({'font_size': 10, 'bold': True})
        format4 = workbook.add_format({'font_size': 10})
        format6 = workbook.add_format({'font_size': 10, 'bold': True})
        format7 = workbook.add_format({'font_size': 10, 'align': 'center'})
        format5 = workbook.add_format({'font_size': 10, 'align': 'right'})
        format1.set_align('center')
        format2.set_align('center')
        format3.set_align('right')
        format4.set_align('left')
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]
        logged_users = self.env['res.company']._company_default_get('account.account')
        report_date = datetime.datetime.now().strftime("%Y-%m-%d")
        sheet.merge_range('M8:N8', "Report Date", format3)
        sheet.merge_range('M9:N9', report_date, format4)
        sheet.merge_range(1, 0, 1, 14, logged_users.name, format4)
        sheet.merge_range(3, 0, 4, 14, "General Ledger Report", format1)
        sheet.merge_range('A6:B6', "Journals :", format6)
        row = 6
        col = 0
        i = 0
        for values in codes:
            sheet.write(row, col+i, values, format7)
            i += 1
        if data['form']['display_account'] == 'all':
            display_account = 'All accounts'
        elif data['form']['display_account'] == 'movement':
            display_account = 'With movements'
        else:
            display_account = 'With balance not equal to zero'

        if data['form']['target_move'] == 'all':
            target_moves = 'All entries'
        else:
            target_moves = 'All posted entries'

        if data['form']['sortby'] == 'sort_date':
            sortby = 'Date'
        else:
            sortby = 'Journal and partners'
        if data['form']['date_from']:
            date_start = data['form']['date_from']
        else:
            date_start = ""
        if data['form']['date_to']:
            date_end = data['form']['date_to']
        else:
            date_end = ""
        if sortby == 'Date':
            sheet.write('G8', "Start Date", format3)
            sheet.write('G9', date_start, format4)
            sheet.write('J8', "End Date", format3)
            sheet.write('J9', date_end, format4)
        sheet.merge_range('C8:D8', "Sorted By", format3)
        sheet.merge_range('C9:D9', sortby, format4)
        sheet.merge_range('A8:B8', "Display Account ", format6)
        sheet.merge_range('A9:B9', display_account, format7)
        sheet.merge_range('E8:F8', "Target Moves", format6)
        sheet.merge_range('E9:F9', target_moves, format7)
        sheet.write('A11', "Date ", format2)
        sheet.write('B11', "JRNL", format2)
        sheet.merge_range('C11:D11', "Partner", format2)
        sheet.merge_range('E11:F11', "Ref", format2)
        sheet.merge_range('G11:H11', "Move", format2)
        sheet.merge_range('I11:L11', "Entry Label", format2)
        sheet.write('M11', "Debit", format2)
        sheet.write('N11', "Credit", format2)
        sheet.write('O11', "Balance", format2)
        accounts = self.env['account.account'].search([])
        row_number = 11
        col_number = 0
        for datas in accounts:
            for values in report_obj:
                if datas['name'] == values['name']:
                    sheet.write(row_number, col_number, datas['code'], format3)
                    sheet.merge_range(row_number, col_number + 1, row_number, col_number + 11, datas['name'], format6)
                    sheet.write(row_number, col_number + 12, logged_users.currency_id.symbol + ' ' + "{:,}".format(values['debit']), format3)
                    sheet.write(row_number, col_number + 13, logged_users.currency_id.symbol + ' ' + "{:,}".format(values['credit']), format3)
                    sheet.write(row_number, col_number + 14, logged_users.currency_id.symbol + ' ' + "{:,}".format(values['balance']), format3)
                    row_number += 1
                    for lines in values['move_lines']:
                        sheet.write(row_number, col_number, lines['ldate'], format4)
                        sheet.write(row_number, col_number + 1, lines['lcode'], format4)
                        sheet.merge_range(row_number, col_number + 2, row_number, col_number + 3, lines['partner_name'], format4)
                        sheet.merge_range(row_number, col_number + 4, row_number, col_number + 5, lines['lref'], format4)
                        sheet.merge_range(row_number, col_number + 6, row_number, col_number + 7, lines['move_name'], format4)
                        sheet.merge_range(row_number, col_number + 8, row_number, col_number + 11, lines['lname'], format4)
                        sheet.write(row_number, col_number + 12, "{:,}".format(lines['debit']), format5)
                        sheet.write(row_number, col_number + 13,  "{:,}".format(lines['credit']), format5)
                        sheet.write(row_number, col_number + 14,  "{:,}".format(lines['balance']), format5)
                        row_number += 1
