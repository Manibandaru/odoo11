# -*- coding: utf-8 -*-
import logging
from odoo import models


class PartnerLedgerReportXlsx(models.AbstractModel):
    _name = "report.account_reports_xlsx.partner_ledger_report_xls"
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
        data['form']['used_context'] = {}
        data['form']['used_context']['date_to'] = vals['date_to']
        data['form']['used_context']['date_from'] = vals['date_from']
        data['form']['used_context']['journal_ids'] = data['form']['journal_ids']
        data['form']['used_context']['state'] = 'posted'
        data['form']['used_context']['strict_range'] = True
        env_obj = vals.env['report.account.report_partnerledger']

        data['computed'] = {}

        obj_partner = env_obj.env['res.partner']
        query_get_data = env_obj.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']
        env_obj.env.cr.execute("""
            SELECT a.id
            FROM account_account a
            WHERE a.internal_type IN %s
            AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in env_obj.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        query = """
            SELECT DISTINCT "account_move_line".partner_id
            FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
            WHERE "account_move_line".partner_id IS NOT NULL
                AND "account_move_line".account_id = account.id
                AND am.id = "account_move_line".move_id
                AND am.state IN %s
                AND "account_move_line".account_id IN %s
                AND NOT account.deprecated
                AND """ + query_get_data[1] + reconcile_clause
        env_obj.env.cr.execute(query, tuple(params))
        # ---------------------Taking only selected partners---------------------------
        if data['form']['partner_ids']:
            partner_ids = data['form']['partner_ids']
        else:
            partner_ids = [res['partner_id'] for res in env_obj.env.cr.dictfetchall()]
        # -----------------------------------------------------------------------------
        # partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]
        partners = obj_partner.browse(partner_ids)
        partners = sorted(partners, key=lambda x: (x.name or ''))
        # partners = sorted(partners, key=lambda x: (x.uniqueid or '', x.name or ''))
        for items in partners:
            partner_currency_balance = 0
            sheet = workbook.add_worksheet(str(items.name))
            format1 = workbook.add_format({'font_size': 16, 'align': 'center', 'bg_color': '#D3D3D3', 'bold': True})
            format1.set_font_color('#000080')
            format2 = workbook.add_format({'font_size': 12, 'bold': True})
            format3 = workbook.add_format({'font_size': 10, 'bold': True})
            format4 = workbook.add_format({'font_size': 10})
            format5 = workbook.add_format({'font_size': 10})
            format6 = workbook.add_format({'font_size': 10, 'bold': True})
            format7 = workbook.add_format({'font_size': 10, 'bold': True})
            format8 = workbook.add_format({'font_size': 10})
            format9 = workbook.add_format({'font_size': 10})
            format10 = workbook.add_format({'font_size': 10, 'bold': True})
            format1.set_align('center')
            format3.set_align('center')
            format4.set_align('center')
            format6.set_align('right')
            currency = self.env.user.company_id.currency_id.symbol
            format7.set_num_format('0.00 ' + currency)
            format8.set_num_format('0.00 ' + currency)
            logged_users = self.env['res.company']._company_default_get('account.account')
            sheet.merge_range('A1:B1', logged_users.name, format4)
            if data['form']['date_from']:
                sheet.write('E2', 'Date from:', format6)
                sheet.write('F2', data['form']['date_from'], format5)
            if data['form']['date_to']:
                sheet.write('E3', 'Date to:', format6)
                sheet.write('F3', data['form']['date_to'], format5)
            sheet.merge_range('I2:J2', 'Target Moves:', format6)
            if data['form']['target_move'] == 'all':
                sheet.merge_range('K2:L2', 'All Entries', format4)
            if data['form']['target_move'] == 'posted':
                sheet.merge_range('K2:L2', 'All Posted Entries', format4)
            sheet.merge_range(5, 0, 5, 1, "Date", format3)
            sheet.merge_range(5, 2, 5, 3, "JRNL", format3)
            sheet.merge_range(5, 4, 5, 5, "Account", format3)
            sheet.merge_range(5, 6, 5, 7, "Ref", format3)
            sheet.merge_range(5, 8, 5, 9, "Debit", format3)
            sheet.merge_range(5, 10, 5, 11, "Credit", format3)
            sheet.merge_range(5, 12, 5, 13, "Balance", format3)
            if data['form']['amount_currency']:
                sheet.merge_range(5, 14, 5, 15, "Currency", format3)
                sheet.merge_range(3, 0, 4, 15, "Partner Ledger Report", format1)
            else:
                sheet.merge_range(3, 0, 4, 13, "Partner Ledger Report", format1)
            partner_name = ''
            # if items.uniqueid:
            #     partner_name = str(items.uniqueid)
            if items.name:
                partner_name = partner_name + str(items.name)
            sheet.merge_range(6, 0, 6, 6, partner_name, format2)
            debit = env_obj._sum_partner(data, items, 'debit')
            credit = env_obj._sum_partner(data, items, 'credit')
            balance = env_obj._sum_partner(data, items, 'debit - credit')
            sheet.merge_range(6, 8, 6, 9, debit, format7)
            sheet.merge_range(6, 10, 6, 11, credit, format7)
            sheet.merge_range(6, 12, 6, 13, balance, format7)
            row_value = 7
            for values in env_obj._lines(data, items):
                sheet.merge_range(row_value, 0, row_value, 1, values['date'], format4)
                sheet.merge_range(row_value, 2, row_value, 3, values['code'], format4)
                sheet.merge_range(row_value, 4, row_value, 5, values['a_code'], format4)
                sheet.merge_range(row_value, 6, row_value, 7, values['displayed_name'], format4)
                sheet.merge_range(row_value, 8, row_value, 9, values['debit'], format8)
                sheet.merge_range(row_value, 10, row_value, 11, values['credit'], format8)
                sheet.merge_range(row_value, 12, row_value, 13, values['progress'], format8)
                if data['form']['amount_currency']:
                    if values['currency_id']:
                        partner_currency = values['currency_id'].symbol
                        format9.set_num_format('0.00 ' + partner_currency)
                        format10.set_num_format('0.00 ' + partner_currency)
                        sheet.merge_range(row_value, 14, row_value, 15, values['amount_currency'], format9)
                        partner_currency_balance += values['amount_currency']
                        sheet.merge_range(6, 14, 6, 15, partner_currency_balance, format10)
                row_value += 1
