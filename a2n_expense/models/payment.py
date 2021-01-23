# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare
from datetime import datetime

from itertools import groupby




class account_voucher_custom(models.Model):
    _inherit = "account.voucher"

    account_id = fields.Many2one('account.account', 'Account',default=None,
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 domain="[('deprecated', '=', False),('user_type_id','=',3)]")

    @api.multi
    def voucher_move_line_create(self, line_total, move_id, company_currency, current_currency):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        for line in self.line_ids:
            # create one move line per voucher line where amount is not 0.0
            if not line.price_subtotal:
                continue
            line_subtotal = line.price_subtotal
            if self.voucher_type == 'sale':
                line_subtotal = -1 * line.price_subtotal
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context,
            # so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(line.price_unit * line.quantity)
            move_line = {
                'journal_id': self.journal_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': line.partner_id.id or self.partner_id.commercial_partner_id.id,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': abs(amount) if self.voucher_type == 'sale' else 0.0,
                'debit': abs(amount) if self.voucher_type == 'purchase' else 0.0,
                'date': self.account_date,
                'tax_ids': [(4, t.id) for t in line.tax_ids],
                'amount_currency': line_subtotal if current_currency != company_currency else 0.0,
                'currency_id': company_currency != current_currency and current_currency or False,
                'payment_id': self._context.get('payment_id'),
            }
            self.env['account.move.line'].with_context(apply_taxes=True).create(move_line)
        return line_total


class account_voucher_line(models.Model):
    _inherit = "account.voucher.line"


    partner_id = fields.Many2one('res.partner',string='Partner')








class AccountPayment(models.Model):
    _inherit = 'account.payment'

    account_id = fields.Many2one('account.account',string='Account')

    def _get_liquidity_move_line_vals(self, amount):
        name = self.name
        if self.payment_type == 'transfer':
            name = _('Transfer to %s') % self.destination_journal_id.name
        if self.account_id:
            account = self.account_id.id
        else:
            account = self.payment_type in ('outbound',
                                                'transfer') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id

        vals = {
            'name': name,
            'account_id': account,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id.with_context(date=self.payment_date).compute(amount, self.journal_id.currency_id)
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(
                date=self.payment_date).compute_amount_fields(amount, self.journal_id.currency_id,
                                                              self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })

        return vals
