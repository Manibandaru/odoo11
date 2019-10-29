# -*- encoding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2012 (http://www.globalteckz.com)
#
##############################################################################
import time
from odoo import api, fields, models, _
from datetime import datetime, timedelta
#import DateTime
from odoo.tools.translate import _
from odoo.exceptions import UserError


class account_statement_report(models.TransientModel):

	_name = "account.statement.report"
	_description = "Customer Account Statement Report"

	@api.multi
	def _get_ids(self):
		if self._context.get('active_ids'):
			return self._context.get('active_ids')
		return False

	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
	period_from = fields.Date(string='From', required=True, default=lambda *a: time.strftime('%Y-01-01'))
	period_to = fields.Date(string='To', required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
	# ageing_type = fields.Selection([('limited_period', 'Limited Period(Upto 5+)'),
	# 								('monthly', 'Monthly'),
	# 								('days', 'Days Bases')], string='Ageing Type',
	# 								required=True, domain="[('company_id','=',company_id)]")
	partner_ids = fields.Many2many('res.partner','partner_statement_rel','partner_id','statement_id','Partners', default=_get_ids)
	ageing_length = fields.Integer('Days Length' ,required=True, default= 30)
	# target_mv = fields.Selection([('post_entry', 'All Posted Entries'),
	# 								('unpost_entry', 'All Entries')], string='Target Moves',
	# 								required=True, default='post_entry')
	# journal_ids = fields.Many2many('account.journal', 'acc_journal_rel', 'journals', 'journal_id', string='Journal Type', required=True)


	@api.multi
	def print_report(self):
		if self.period_from > self.period_to:
			raise UserError(_('The start date must be anterior to the end date.'))
		return self.env.ref('gt_customer_account_statement.action_cus_sup_report').report_action(self)

	@api.multi
	def ids_to_objects(self):
		all_lines = []
		for partner in self.partner_ids:
			line_ids = self.env['res.partner'].search([('name','=',partner.name)])
			for line in line_ids:
				if line not in all_lines:
					all_lines.append(line)
		return all_lines

	def sortDictBy(self,list, key):
		nlist = sorted(list, key=lambda x: (x[key], x))
		return nlist

	@api.multi
	def lines(self, partner_id):
		self.post_dated_cheque = []
		self.balance = 0.0
		self.balance_bf = 0.0
		self.ageing_list_days = []
		self.total_debit = 0.0
		self.total_credit = 0.0
		self.total_balance = 0.0
		self.sum_balance = 0.0
		self.sum_debit = 0.0
		self.sum_credit = 0.0
		result_bal=[]
		res = {}
        
		inv_obj = self.env['account.invoice']
		account_mv_obj = self.env['account.move.line']
		company_currency = self.company_id.currency_id

		start_limit = 0
		end_limit = 0
		for p1 in  range(0,5):
			r1 = {}
			start_limit = end_limit
			end_limit += self.ageing_length
			r1['name'] = str(start_limit)+"-"+str(end_limit)
			r1['amount'] = 0.0
			if p1 == 3:
				end_limit -= self.ageing_length
				r1['name'] = str(end_limit) + "+"
			if p1 == 4:
				r1['name'] = 'Total'
			self.ageing_list_days.append(r1)
        
		inv_ids = inv_obj.search([('date_invoice','<',self.period_from),
			('partner_id','=',partner_id),
			('type','in',['out_invoice','out_refund']),
			('state', 'in', ['open','paid']),
			('company_id','=',self.company_id.id)
			])

		#Calculating Balance B/F

		bf_bal = 0.00
		movelines = account_mv_obj.search([('journal_id.type','=','situation'),
			('move_id.date','<=',self.period_to),
			('partner_id','=',partner_id)], order='date')

		if movelines:
			for line in movelines:

				bf_bal += line.debit - line.credit
				date = line.date_maturity or line.date
				condition_1 = (datetime.strptime(date, '%Y-%m-%d') >= datetime.strptime(self.period_from, '%Y-%m-%d'))
				condition_2 = (datetime.strptime(date, '%Y-%m-%d') <= datetime.strptime(self.period_to, '%Y-%m-%d'))
				diff_date=datetime.strptime(self.period_to, '%Y-%m-%d') - datetime.strptime(date, '%Y-%m-%d')
				diff=diff_date.days
				pass_amount = line.debit - line.credit
				age_length = self.ageing_length
                # if form['ageing_type'] == 'days':
				if diff <= age_length:
					self.ageing_list_days[0]['amount'] += pass_amount
					self.ageing_list_days[4]['amount'] += pass_amount
				elif (diff > age_length and diff <= age_length * 2):
					self.ageing_list_days[1]['amount'] += pass_amount
					self.ageing_list_days[4]['amount'] += pass_amount
				elif (diff > age_length * 2 and diff <= age_length * 3): 
					self.ageing_list_days[2]['amount'] += pass_amount
					self.ageing_list_days[4]['amount'] += pass_amount
				elif (diff > age_length * 3 ): 
					self.ageing_list_days[3]['amount'] += pass_amount
					self.ageing_list_days[4]['amount'] += pass_amount

                        
		if inv_ids:
			for invoice_id in inv_ids:
				s_list = []
				s_final = []
				for move_line in invoice_id.move_id.line_ids:
					if move_line.account_id.id == invoice_id.account_id.id:
						s_dict = {}
						test_date = move_line.date_maturity or move_line.date
						s_dict['date'] = test_date
						s_dict['value'] = move_line
						s_list.append(s_dict)

				s_list = self.sortDictBy(s_list, 'date')

				for s in s_list:
					s_final.append(s['value'])
                
				remaining_amt = 0.0
				payments = invoice_id.payment_move_line_ids
				# payments and payments.reverse()
				done_list = []

				for line_b in s_final:
					bf_bal += line_b.debit or 0.0
					date = line_b.date_maturity or line_b.date
					condition_1 = (datetime.strptime(date, '%Y-%m-%d') >= datetime.strptime(self.period_from, '%Y-%m-%d'))
					condition_2 = (datetime.strptime(date, '%Y-%m-%d') <= datetime.strptime(self.period_to, '%Y-%m-%d'))
                    
					if condition_1 and  condition_2:

						diff_date=datetime.strptime(self.period_from, '%Y-%m-%d') - datetime.strptime(date, '%Y-%m-%d')
						diff=diff_date.days
						pass_amount = line_b.debit - line_b.credit
                        
						for pay_b in payments:
							if pass_amount > 0.0:
								date = pay_b.date
								condition_3 = (datetime.strptime(date, '%Y-%m-%d') >= datetime.strptime(self.period_from, '%Y-%m-%d'))
								condition_4 = (datetime.strptime(date, '%Y-%m-%d') <= datetime.strptime(self.period_to, '%Y-%m-%d'))
								if condition_3 and condition_4:
									pass_amount += pay.debit - pay.credit
                        
						age_length = self.ageing_length
						# if form['ageing_type'] == 'days':
						if diff <= self.age_length:
							self.ageing_list_days[0]['amount'] += pass_amount
							self.ageing_list_days[4]['amount'] += pass_amount
						elif (diff > age_length and diff <= age_length * 2):
							self.ageing_list_days[1]['amount'] += pass_amount
							self.ageing_list_days[4]['amount'] += pass_amount
						elif (diff > age_length * 2 and diff <= age_length * 3): 
							self.ageing_list_days[2]['amount'] += pass_amount
							self.ageing_list_days[4]['amount'] += pass_amount
						elif (diff > age_length * 3 ): 
							self.ageing_list_days[3]['amount'] += pass_amount
							self.ageing_list_days[4]['amount'] += pass_amount


				for pay_b in payments:
					if pay_b.date > self.period_to:
						account = False
						if pay_b.move_id:
							for pay_line in pay_b.move_id.line_id:
								if pay_b.credit and pay_line.debit:
									account = pay_line.account_id.name
								elif pay_b.debit and pay_line.credit:
									account = pay_line.account_id.name
                        
						res_b = {
							'date' : pay_b.date,
							'maturity_date':pay_b.date_maturity or '',
							'ref': pay_b.ref,
							'desc': pay_b.narration or account +"-"+  pay_b.name,
							'debit': '',
							'credit':pay_b.debit or pay_b.credit,
							'balance' : 0.0,
							'currency': (pay_b.currency_id and pay_b.currency_id.symbol or pay_b.currency_id.name) or (company_currency and company_currency.symbol or company_currency.name),
							'amount_currency': pay_b.amount_currency and pay_b.amount_currency or pay_b.debit - pay_b.credit 
							}
						self.total_credit += (pay_b.debit or pay_b.credit)
						self.post_dated_cheque.append(res_b)
					else:
						if pay_b.credit:
							bf_bal -= pay_b.credit or 0.0
						elif pay_b.debit:
							bf_bal += pay_b.debit or 0.0
                            
		tmp = {
			'date' : '',
			'maturity_date':'',
			'ref' : '',
			'desc' : 'Balance B/F',
			'debit' : bf_bal > 0.0 and bf_bal or 0.00,
			'credit' :bf_bal < 0.0 and abs(bf_bal) or 0.00,
			'balance' : bf_bal,
			'currency': company_currency and company_currency.symbol or company_currency.name,
			'amount_currency': bf_bal
			}
		self.total_debit += (bf_bal > 0.0 and bf_bal or 0.00)
		self.total_credit += (bf_bal < 0.0 and abs(bf_bal) or 0.00)
		result_bal.append(tmp)
		self.balance_bf = bf_bal

		#calculating month vice or date wise balance

		partner = self.env['res.partner'].browse(partner_id)
		movelines = account_mv_obj.search([
						('journal_id.type','in',['cash','bank']),
						('move_id.date','<=',self.period_to),
						('partner_id','=',partner_id),
						('account_id','=', partner.property_account_receivable_id.id)], order='date')
		# if movelines:
		# 	for line in movelines:
		# 		self.balance += line.debit - line.credit
		# 		res = {
		# 		'date' : line.date,
		# 		'maturity_date':line.date_maturity or '',
		# 		'ref': line.ref,
		# 		'desc': line.narration or line.name,
		# 		'debit': line.debit or 0.0,
		# 		'credit': line.credit or 0.0,
		# 		'balance' : self.balance_bf + self.balance,
		# 		'currency': (line.currency_id and line.currency_id.symbol or line.currency_id.name) or (company_currency and company_currency.symbol or company_currency.name),
		# 		'amount_currency': line.amount_currency and line.amount_currency or (line.debit - line.credit)
		# 		}

		# 		result_bal.append(res)
		# 		date = line.date_maturity or line.date
		# 		diff_date=datetime.strptime(self.period_to, '%Y-%m-%d') - datetime.strptime(date, '%Y-%m-%d')
		# 		diff=diff_date.days
		# 		self.total_debit += line.debit
		# 		self.total_credit += line.credit
				
		# 		pass_amount = line.debit - line.credit
                
		# 		age_length = self.ageing_length
		# 		# if form['ageing_type'] == 'days':
                
		# 		if diff <= age_length:
		# 			self.ageing_list_days[0]['amount'] += pass_amount
		# 			self.ageing_list_days[4]['amount'] += pass_amount
		# 		elif (diff > age_length and diff <= age_length * 2):
		# 			self.ageing_list_days[1]['amount'] += pass_amount
		# 			self.ageing_list_days[4]['amount'] += pass_amount
		# 		elif (diff > age_length * 2 and diff <= age_length * 3): 
		# 			self.ageing_list_days[2]['amount'] += pass_amount
		# 			self.ageing_list_days[4]['amount'] += pass_amount
		# 		elif (diff > age_length * 3 ): 
		# 			self.ageing_list_days[3]['amount'] += pass_amount
		# 			self.ageing_list_days[4]['amount'] += pass_amount
                            

		payments = []
		account_invoices = inv_obj.search([('type','in',['out_invoice','out_refund']), 
							('state', 'in', ('open','paid')),
							('partner_id','=',partner_id),
							('date_invoice','>=',self.period_from),
							('date_invoice','<=',self.period_to),
							('company_id','=',self.company_id.id)], order='date_invoice')
		if account_invoices:
			for invoice in account_invoices:
				res={}
				s_list = []
				s_final = []
				for move_line in invoice.move_id.line_ids:
					if move_line.account_id.id == invoice.account_id.id:
						s_dict = {}
						test_date = move_line.date_maturity or move_line.date
						s_dict['date'] = test_date
						s_dict['value'] = move_line
						s_list.append(s_dict)
				s_list = self.sortDictBy(s_list, 'date')
				for s in s_list:
					s_final.append(s['value'])

				remaining_amt = 0.0
				payments = invoice.payment_move_line_ids
                # payments and payments.reverse()
				done_list1 = []
				for line in s_final:
					self.balance += line.debit - line.credit
					res = {
						'date' :line.date,
						'maturity_date':line.date_maturity or '',
						'ref': line.ref,
						'desc': invoice.comment  or '' +"-"+ line.name or '',
						'debit': line.debit or 0.0,
						'credit':line.credit or 0.0,
						'balance' : self.balance_bf + self.balance,
						'currency': (line.currency_id and line.currency_id.symbol) or (company_currency and company_currency.symbol or company_currency.name),
						'amount_currency': line.amount_currency and line.amount_currency or (line.debit - line.credit)
						}
					self.total_balance += self.balance_bf + self.balance
					self.total_debit += line.debit
					self.total_credit += line.credit
					result_bal.append(res)
					date = line.date_maturity or line.date

					condition_1 = (datetime.strptime(date, '%Y-%m-%d') >= datetime.strptime(self.period_from, '%Y-%m-%d'))
					condition_2 = (datetime.strptime(date, '%Y-%m-%d') <= datetime.strptime(self.period_to, '%Y-%m-%d'))
					                    
					if condition_1 and  condition_2:
						diff_date=datetime.strptime(self.period_to, '%Y-%m-%d') - datetime.strptime(date, '%Y-%m-%d')
						diff=diff_date.days
						pass_amount = line.debit - line.credit
						for pay in payments:
							pass_amount += pay.debit - pay.credit
						age_length = self.ageing_length
						# if form['ageing_type'] == 'days':
						if diff <= age_length:
							self.ageing_list_days[0]['amount'] += pass_amount
							self.ageing_list_days[4]['amount'] += pass_amount
						elif (diff > age_length and diff <= age_length * 2):
							self.ageing_list_days[1]['amount'] += pass_amount
							self.ageing_list_days[4]['amount'] += pass_amount
						elif (diff > age_length * 2 and diff <= age_length * 3): 
							self.ageing_list_days[2]['amount'] += pass_amount
							self.ageing_list_days[4]['amount'] += pass_amount
						elif (diff > age_length * 3 ): 
							self.ageing_list_days[3]['amount'] += pass_amount
							self.ageing_list_days[4]['amount'] += pass_amount
                                
               
				for pay in payments:
					account = False
					if pay.move_id:
						for pay_line in pay.move_id.line_ids:
							if pay.credit and pay_line.debit:
								account = pay_line.account_id.name
							elif pay.debit and pay_line.credit:
								account = pay_line.account_id.name
                                
					res = {
						'date' : pay.date,
						'maturity_date':pay.date_maturity or '',
						'ref': pay.ref,
						'desc': pay.narration or str(account)+"-"+str(pay.name),
						'debit': pay.debit or 0.0,
						'credit':pay.credit or 0.0,
						'balance' : 0.0,
						'currency': (pay.currency_id and pay.currency_id.symbol) or (company_currency and company_currency.symbol or company_currency.name),
						'amount_currency': pay.amount_currency and pay.amount_currency or (pay.debit - pay.credit)
						}
					self.total_balance += 0.0
					self.total_debit += pay.debit
					self.total_credit += pay.credit
					if pay.date > self.period_to:
						self.post_dated_cheque.append(res)
					else:
						if pay.credit:
							self.balance -= pay.credit or 0.0
						elif pay.debit:
							self.balance += pay.debit or 0.0

						res['balance'] = self.balance_bf + self.balance
						result_bal.append(res)
		if result_bal:
			result_bal = sorted(result_bal, key=lambda k: k['date'])
			for dict1 in result_bal:
				self.sum_balance += (dict1.get('debit') or 0.0)
				self.sum_debit += (dict1.get('debit') or 0.0)
				self.sum_credit += (dict1.get('credit') and float(dict1.get('credit')) or 0.0)
				self.sum_balance -= (dict1.get('credit') or 0.0)
				dict1.update({'balance': (self.sum_balance and self.sum_balance < 0 and ('(' + str(abs(self.sum_balance)) + ')')) or self.sum_balance})
		result_bal = result_bal or [{}]
		return result_bal

		# >>>>>>>>>>>>>SUPPLIERRRRRRRRRR>>>>>>>>>>>>>>>>>>>>


	@api.multi
	def supplier_lines(self, partner_id):
		self.post_dated_cheque = []
		self.balance = 0.0
		self.balance_bf = 0.0
		self.ageing_list_days = []
		self.total_debit = 0.0
		self.total_credit = 0.0
		self.total_balance = 0.0
		self.sum_balance = 0.0
		self.sum_debit = 0.0
		self.sum_credit = 0.0
		result_bal=[]
		res = {}
        
		inv_obj = self.env['account.invoice']
		account_mv_obj = self.env['account.move.line']
		company_currency = self.company_id.currency_id

		start_limit = 0
		end_limit = 0
		for p1 in  range(0,5):
			r1 = {}
			start_limit = end_limit
			end_limit += self.ageing_length
			r1['name'] = str(start_limit)+"-"+str(end_limit)
			r1['amount'] = 0.0
			if p1 == 3:
				end_limit -= self.ageing_length
				r1['name'] = str(end_limit) + "+"
			if p1 == 4:
				r1['name'] = 'Total'
			self.ageing_list_days.append(r1)
        
		inv_ids = inv_obj.search([('date_invoice','<',self.period_from),
			('partner_id','=',partner_id),
			('type','in',['in_invoice','in_refund']),
			('state', 'in', ['open','paid']),
			('company_id','=',self.company_id.id)
			])

		#Calculating Balance B/F

		bf_bal = 0.00
		movelines = account_mv_obj.search([('journal_id.type','=','situation'),
			('move_id.date','<=',self.period_to),
			('partner_id','=',partner_id)], order='date')

		if movelines:
			for line in movelines:

				bf_bal +=  line.credit - line.debit 
				date = line.date_maturity or line.date
				condition_1 = (datetime.strptime(date, '%Y-%m-%d') >= datetime.strptime(self.period_from, '%Y-%m-%d'))
				condition_2 = (datetime.strptime(date, '%Y-%m-%d') <= datetime.strptime(self.period_to, '%Y-%m-%d'))
				diff_date=datetime.strptime(self.period_to, '%Y-%m-%d') - datetime.strptime(date, '%Y-%m-%d')
				diff=diff_date.days
				pass_amount =  line.credit - line.debit
				age_length = self.ageing_length
                # if form['ageing_type'] == 'days':
				if diff <= age_length:
					self.ageing_list_days[0]['amount'] += pass_amount
					self.ageing_list_days[4]['amount'] += pass_amount
				elif (diff > age_length and diff <= age_length * 2):
					self.ageing_list_days[1]['amount'] += pass_amount
					self.ageing_list_days[4]['amount'] += pass_amount
				elif (diff > age_length * 2 and diff <= age_length * 3): 
					self.ageing_list_days[2]['amount'] += pass_amount
					self.ageing_list_days[4]['amount'] += pass_amount
				elif (diff > age_length * 3 ): 
					self.ageing_list_days[3]['amount'] += pass_amount
					self.ageing_list_days[4]['amount'] += pass_amount

                        
		if inv_ids:
			for invoice_id in inv_ids:
				s_list = []
				s_final = []
				for move_line in invoice_id.move_id.line_ids:
					if move_line.account_id.id == invoice_id.account_id.id:
						s_dict = {}
						test_date = move_line.date_maturity or move_line.date
						s_dict['date'] = test_date
						s_dict['value'] = move_line
						s_list.append(s_dict)

				s_list = self.sortDictBy(s_list, 'date')

				for s in s_list:
					s_final.append(s['value'])
                
				remaining_amt = 0.0
				payments = invoice_id.payment_move_line_ids
				# payments and payments.reverse()
				done_list = []

				for line_b in s_final:
					bf_bal += line_b.credit or 0.0
					date = line_b.date_maturity or line_b.date
					condition_1 = (datetime.strptime(date, '%Y-%m-%d') >= datetime.strptime(self.period_from, '%Y-%m-%d'))
					condition_2 = (datetime.strptime(date, '%Y-%m-%d') <= datetime.strptime(self.period_to, '%Y-%m-%d'))
                    
					if condition_1 and  condition_2:

						diff_date=datetime.strptime(self.period_from, '%Y-%m-%d') - datetime.strptime(date, '%Y-%m-%d')
						diff=diff_date.days
						pass_amount = line_b.credit - line_b.debit
                        
						for pay_b in payments:
							if pass_amount > 0.0:
								date = pay_b.date
								condition_3 = (datetime.strptime(date, '%Y-%m-%d') >= datetime.strptime(self.period_from, '%Y-%m-%d'))
								condition_4 = (datetime.strptime(date, '%Y-%m-%d') <= datetime.strptime(self.period_to, '%Y-%m-%d'))
								if condition_3 and condition_4:
									pass_amount +=  pay.credit - pay.debit
                        
						age_length = self.ageing_length
						# if form['ageing_type'] == 'days':
						if diff <= self.age_length:
							self.ageing_list_days[0]['amount'] += pass_amount
							self.ageing_list_days[4]['amount'] += pass_amount
						elif (diff > age_length and diff <= age_length * 2):
							self.ageing_list_days[1]['amount'] += pass_amount
							self.ageing_list_days[4]['amount'] += pass_amount
						elif (diff > age_length * 2 and diff <= age_length * 3): 
							self.ageing_list_days[2]['amount'] += pass_amount
							self.ageing_list_days[4]['amount'] += pass_amount
						elif (diff > age_length * 3 ): 
							self.ageing_list_days[3]['amount'] += pass_amount
							self.ageing_list_days[4]['amount'] += pass_amount


				for pay_b in payments:
					if pay_b.date > self.period_to:
						account = False
						if pay_b.move_id:
							for pay_line in pay_b.move_id.line_id:
								if pay_b.credit and pay_line.debit:
									account = pay_line.account_id.name
								elif pay_b.debit and pay_line.credit:
									account = pay_line.account_id.name
                        
						res_b = {
							'date' : pay_b.date,
							'maturity_date':pay_b.date_maturity or '',
							'ref': pay_b.ref,
							'desc': pay_b.narration or account +"-"+  pay_b.name,
							'debit': '',
							'credit':pay_b.debit or pay_b.credit,
							'balance' : 0.0,
							'currency': (pay_b.currency_id and pay_b.currency_id.symbol or pay_b.currency_id.name) or (company_currency and company_currency.symbol or company_currency.name),
							'amount_currency': pay_b.amount_currency and pay_b.amount_currency or pay_b.debit - pay_b.credit 
							}
						self.total_credit += (pay_b.debit or pay_b.credit)
						self.post_dated_cheque.append(res_b)
					else:
						if pay_b.credit:
							bf_bal += pay_b.credit or 0.0
						elif pay_b.debit:
							bf_bal -= pay_b.debit or 0.0
                            
		tmp = {
			'date' : '',
			'maturity_date':'',
			'ref' : '',
			'desc' : 'Balance B/F',
			'debit' : bf_bal > 0.0 and bf_bal or 0.00,
			'credit' :bf_bal < 0.0 and abs(bf_bal) or 0.00,
			'balance' : bf_bal,
			'currency': company_currency and company_currency.symbol or company_currency.name,
			'amount_currency': bf_bal
			}
		self.total_debit += (bf_bal > 0.0 and bf_bal or 0.00)
		self.total_credit += (bf_bal < 0.0 and abs(bf_bal) or 0.00)
		result_bal.append(tmp)
		self.balance_bf = bf_bal

		#calculating month vice or date wise balance

		partner = self.env['res.partner'].browse(partner_id)
		movelines = account_mv_obj.search([
						('journal_id.type','in',['cash','bank']),
						('move_id.date','<=',self.period_to),
						('partner_id','=',partner_id),
						('account_id','=', partner.property_account_payable_id.id)], order='date')
		# if movelines:
		# 	for line in movelines:
		# 		self.balance += line.credit - line.debit
		# 		res = {
		# 		'date' : line.date,
		# 		'maturity_date':line.date_maturity or '',
		# 		'ref': line.ref,
		# 		'desc': line.narration or line.name,
		# 		'debit': line.debit or 0.0,
		# 		'credit': line.credit or 0.0,
		# 		'balance' : self.balance_bf + self.balance,
		# 		'currency': (line.currency_id and line.currency_id.symbol or line.currency_id.name) or (company_currency and company_currency.symbol or company_currency.name),
		# 		'amount_currency': line.amount_currency and line.amount_currency or (line.credit - line.debit)
		# 		}

		# 		result_bal.append(res)
		# 		date = line.date_maturity or line.date
		# 		diff_date=DateTime.strptime(self.period_to, '%Y-%m-%d') - DateTime.strptime(date, '%Y-%m-%d')
		# 		diff=diff_date.days
		# 		self.total_debit += line.debit
		# 		self.total_credit += line.credit
		# 		pass_amount =  line.credit - line.debit
                
		# 		age_length = self.ageing_length
		# 		# if form['ageing_type'] == 'days':
                
		# 		if diff <= age_length:
		# 			self.ageing_list_days[0]['amount'] += pass_amount
		# 			self.ageing_list_days[4]['amount'] += pass_amount
		# 		elif (diff > age_length and diff <= age_length * 2):
		# 			self.ageing_list_days[1]['amount'] += pass_amount
		# 			self.ageing_list_days[4]['amount'] += pass_amount
		# 		elif (diff > age_length * 2 and diff <= age_length * 3): 
		# 			self.ageing_list_days[2]['amount'] += pass_amount
		# 			self.ageing_list_days[4]['amount'] += pass_amount
		# 		elif (diff > age_length * 3 ): 
		# 			self.ageing_list_days[3]['amount'] += pass_amount
		# 			self.ageing_list_days[4]['amount'] += pass_amount
                            

		payments = []
		account_invoices = inv_obj.search([('type','in',['in_invoice','in_refund']), 
							('state', 'in', ('open','paid')),
							('partner_id','=',partner_id),
							('date_invoice','>=',self.period_from),
							('date_invoice','<=',self.period_to),
							('company_id','=',self.company_id.id)], order='date_invoice')
		if account_invoices:
			for invoice in account_invoices:
				res={}
				s_list = []
				s_final = []
				for move_line in invoice.move_id.line_ids:
					if move_line.account_id.id == invoice.account_id.id:
						s_dict = {}
						test_date = move_line.date_maturity or move_line.date
						s_dict['date'] = test_date
						s_dict['value'] = move_line
						s_list.append(s_dict)
				s_list = self.sortDictBy(s_list, 'date')
				for s in s_list:
					s_final.append(s['value'])

				remaining_amt = 0.0
				payments = invoice.payment_move_line_ids
                # payments and payments.reverse()
				done_list1 = []
				for line in s_final:
					self.balance +=  line.credit - line.debit
					res = {
						'date' :line.date,
						'maturity_date':line.date_maturity or '',
						'ref': line.ref,
						'desc': invoice.comment  or '' +"-"+ line.name or '',
						'debit': line.debit or 0.0,
						'credit':line.credit or 0.0,
						'balance' : self.balance_bf + self.balance,
						'currency': (line.currency_id and line.currency_id.symbol) or (company_currency and company_currency.symbol or company_currency.name),
						'amount_currency': line.amount_currency and line.amount_currency or (line.credit - line.debit)
						}
					self.total_balance += self.balance_bf + self.balance
					self.total_debit += line.debit
					self.total_credit += line.credit
					result_bal.append(res)
					date = line.date_maturity or line.date

					
					condition_1 = (DateTime.strptime(date, '%Y-%m-%d') >= datetime.strptime(self.period_from, '%Y-%m-%d'))
					condition_2 = (datetime.strptime(date, '%Y-%m-%d') <= datetime.strptime(self.period_to, '%Y-%m-%d'))
					                    
					if condition_1 and  condition_2:
						diff_date=datetime.strptime(self.period_to, '%Y-%m-%d') - datetime.strptime(date, '%Y-%m-%d')
						diff=diff_date.days
						pass_amount =  line.credit - line.debit
						for pay in payments:
							pass_amount +=  pay.credit - pay.debit
						age_length = self.ageing_length
						# if form['ageing_type'] == 'days':
						if diff <= age_length:
							self.ageing_list_days[0]['amount'] += pass_amount
							self.ageing_list_days[4]['amount'] += pass_amount
						elif (diff > age_length and diff <= age_length * 2):
							self.ageing_list_days[1]['amount'] += pass_amount
							self.ageing_list_days[4]['amount'] += pass_amount
						elif (diff > age_length * 2 and diff <= age_length * 3): 
							self.ageing_list_days[2]['amount'] += pass_amount
							self.ageing_list_days[4]['amount'] += pass_amount
						elif (diff > age_length * 3 ): 
							self.ageing_list_days[3]['amount'] += pass_amount
							self.ageing_list_days[4]['amount'] += pass_amount
                                
               
				for pay in payments:
					account = False
					if pay.move_id:
						for pay_line in pay.move_id.line_ids:
							if pay.credit and pay_line.debit:
								account = pay_line.account_id.name
							elif pay.debit and pay_line.credit:
								account = pay_line.account_id.name
                                
					res = {
						'date' : pay.date,
						'maturity_date':pay.date_maturity or '',
						'ref': pay.ref,
						'desc': pay.narration or str(account)+"-"+str(pay.name),
						'debit': pay.debit or 0.0,
						'credit':pay.credit or 0.0,
						'balance' : 0.0,
						'currency': (pay.currency_id and pay.currency_id.symbol) or (company_currency and company_currency.symbol or company_currency.name),
						'amount_currency': pay.amount_currency and pay.amount_currency or (pay.credit - pay.debit)
						}
					self.total_balance += 0.0
					self.total_debit += pay.debit
					self.total_credit += pay.credit
					if pay.date > self.period_to:
						self.post_dated_cheque.append(res)
					else:
						if pay.credit:
							self.balance += pay.credit or 0.0
						elif pay.debit:
							self.balance -= pay.debit or 0.0

						res['balance'] = self.balance_bf + self.balance
						result_bal.append(res)
		if result_bal:
			result_bal = sorted(result_bal, key=lambda k: k['date'])
			for dict1 in result_bal:
				self.sum_balance += (dict1.get('credit') or 0.0)
				self.sum_debit += (dict1.get('debit') or 0.0)
				self.sum_credit += (dict1.get('credit') and float(dict1.get('credit')) or 0.0)
				self.sum_balance -= (dict1.get('debit') or 0.0)
				dict1.update({'balance': (self.sum_balance and self.sum_balance < 0 and ('(' + str(abs(self.sum_balance)) + ')')) or self.sum_balance})
			
		result_bal = result_bal or [{}]
		return result_bal

	def get_total_credit(self):
		return self.total_credit

	def get_total_debit(self):
		return self.total_debit

	def get_total_balance(self):
		return self.total_balance

	def get_d_ageing(self):
		return self.ageing_list_days

