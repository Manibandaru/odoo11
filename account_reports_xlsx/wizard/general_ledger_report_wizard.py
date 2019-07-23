# -*- encoding: utf-8 -*-
from odoo.osv import orm
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GeneralLedgerReport(orm.TransientModel):
    _inherit = 'account.report.general.ledger'

    active_account = fields.Many2one('account.account', 'Active Account')

    @api.multi
    def report_xlsx(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move'])[0]
        used_context = self.env['account.common.report']._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        return self.print_xlsx_report(data)

    def print_xlsx_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update(self.read(['initial_balance', 'sortby'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            self.error = UserError(_("You must define a Start Date"))
            raise self.error
        context = self._context
        if context.get('active_model'):
            self.active_account = self.env['account.account'].browse(context.get('active_ids')[0])
        return self.env.ref('account_reports_xlsx.ledger_xlsx').with_context(
            landscape=True).report_action(
            self, data=data)

