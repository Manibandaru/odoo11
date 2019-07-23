# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AgedPartnerReport(models.TransientModel):
    _inherit = 'account.aged.trial.balance'

    @api.multi
    def print_xls(self):
        return self.env.ref('account_reports_xlsx.aged_partner_xlsx').report_action(self, data={})
