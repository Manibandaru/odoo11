# -*- encoding: utf-8 -*-
from odoo.osv import orm
from odoo.exceptions import UserError
from odoo import api, fields, models, _


class FinancialReport(models.TransientModel):
    _inherit = 'accounting.report'

    def _print_report(self, data):
        context = self._context
        data['form'].update(self.read(['date_from', 'date_to', 'date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter', 'target_move'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        if context.get('xls_export'):
            return self.env.ref('account_reports_xlsx.accounting_report_xls').report_action(
                self, data=data, config=False)
        else:
            return self.env.ref('account.action_report_financial').report_action(self, data=data, config=False)