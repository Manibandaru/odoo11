from odoo import api, models,fields



class AccountTaxReportUae(models.TransientModel):
    _inherit = "account.common.report"
    _name = 'account.tax.report.uae'
    _description = 'UAE Tax Report'

    def _print_report(self, data):
        return self.env.ref('vat_report.action_report_account_tax_uae').report_action(self, data=data)