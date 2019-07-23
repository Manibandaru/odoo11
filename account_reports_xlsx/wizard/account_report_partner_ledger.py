# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountPartnerLedger(models.TransientModel):
    _inherit = "account.report.partner.ledger"

    partner_ids = fields.Many2many('res.partner', 'partner_ledger_partner_rel', 'id', 'partner_id', string='Partners')

    def _print_report(self, data):
        context = self._context
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency,
                             'partner_ids': self.partner_ids.ids})
        if context.get('xls_export'):
            return self.env.ref('account_reports_xlsx.partner_ledger_xlsx').report_action(self, data=data)
        else:
            return self.env.ref('account.action_report_partnerledger').report_action(self, data=data)
