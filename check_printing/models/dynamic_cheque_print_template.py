# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from openerp import api, models, _
from openerp.exceptions import Warning
import datetime
from textwrap import wrap


#from openerp.addons.dynamic_cheque_print.lang import num2words
from num2words import num2words

class dynamic_cheque_print_template(models.AbstractModel):
	_name = 'report.check_printing.dynamic_cheque_print_template'

	@api.multi
	def get_report_values(self, docids, data=None):

		if not data.get('form').get('label_preview'):

			records = self.env["account.payment"].browse(data["ids"])
			print("*******-----------",records)
		else:
			records = self.env['wizard.cheque.preview'].browse(data['ids'])
		# print("data",data)
		#
		# parameters = {
		# 	'date':self._get_date(records.payment_date),
		# 	'company':self._get_company(data),
		# 	"word_line":self._get_word_line(data,records),
		# 	'get_currency_position': self._get_currency_position(data),
		# 	'num2words': self.get_num2words(data),
		# 	'is_pay_acc': self._is_pay_acc(data),
		# 	#'get_amount':self._get_amount(),
		# 	#'draw_style': self._draw_style()
		#
		# }
		# print("parameters===================12312312312",parameters)

		print("data===",data)
		docargs = {
			'doc_ids': records,
			'doc_model': data['context']['active_model'],
			'docs': records,
			'draw_style': self._draw_style,
			'get_date': self._get_date,
			'get_company': self._get_company,
			'get_signatory_one': self._get_signatory_one,
			'get_word_line': self._get_word_line,
			'get_currency_position': self._get_currency_position,
			'num2words': self.get_num2words,
			'is_pay_acc': self._is_pay_acc,
			'get_amount': self._get_amount,
			'data': data
		}
		print(docargs)
		return docargs

	def _get_date(self, date):
		return datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d%m%Y')

	def _is_pay_acc(self, data):
		if data['form'].get('cheque_format_id'):
			config_id = self.env['dynamic.cheque.format.configuration'].browse([data['form'].get('cheque_format_id')[0]])
			if config_id and config_id.is_ac_pay:
				return True

	def get_num2words(self, data):
		complete_str = ''
		cheque_obj = self.env['dynamic.cheque.format.configuration']
		if not data.get('label_preview'):
			br_rec = self.env['account.payment'].browse([self._context.get('active_id')])
		else:
			br_rec = self.env['wizard.cheque.preview'].browse([data.get('id')])
		amount_total = br_rec.amount
		amount_total = str(amount_total).split('.')
		str1 = num2words(int(amount_total[0]))
		str2 = num2words(int(amount_total[1]))
		if br_rec.currency_id.name == "INR":
			if str1 and str2:
				complete_str = str1 + ' rupee and ' + str2 + ' paisa'
		elif br_rec.currency_id.name == "USD":
			if str1 and str2:
				complete_str = str1 + ' Dollar and ' + str2 + ' Cent'
		elif br_rec.currency_id.name == "AED":
			if str1 and str2:
				complete_str = str1 + ' AED and ' + str2 + ' Fills'
		else:
			complete_str = str1 + ' and ' + str2 + ' Cent'
		if complete_str:
			complete_str += ' only'
		if data and data.get('cheque_format_id'):
			cheque_format_id = cheque_obj.browse([data.get('cheque_format_id')[0]])
			if cheque_format_id and cheque_format_id.amount_word_type == 'standard':
				complete_str = complete_str.title()
			if cheque_format_id and cheque_format_id.amount_word_type == 'capital':
				complete_str = complete_str.upper()
			if cheque_format_id and cheque_format_id.amount_word_type == 'small':
				complete_str = complete_str.lower()
		return complete_str

	def _get_word_line(self, data, record):
		num_words_list = []
		num_words = self.get_num2words(data)
		config_id = self.env['dynamic.cheque.format.configuration'].browse([data.get('cheque_format_id')[0]])
		if config_id:
			if config_id.currency_name:
				if config_id.currency_name_position == 'before':
					num_words = record.currency_id.name + ' ' + num_words
				else:
					num_words = num_words + ' ' + record.currency_id.name
			if config_id and config_id.amount_word_type == 'standard':
				num_words = num_words.title()
			if config_id and config_id.amount_word_type == 'capital':
				num_words = num_words.upper()
			if config_id and config_id.amount_word_type == 'small':
				num_words = num_words.lower()
			if config_id.first_line_words_count > 0:
				num_words_list.append(num_words[0:config_id.first_line_words_count])
			if config_id.second_line_words_count > 0:
				num_words_list.append(num_words[config_id.first_line_words_count:(
							config_id.first_line_words_count + config_id.second_line_words_count)])
		if num_words_list:
			return num_words_list

	def _get_amount(self, amount, display_currency):
	    if display_currency:
	        fmt = "%.{0}f".format(display_currency.decimal_places)
	        lang = self.env['ir.qweb.field'].user_lang()
	        amount = lang.format(fmt, display_currency.round(amount),
	                                       grouping=True, monetary=True).replace(r' ', u'\N{NO-BREAK SPACE}')
	    return amount

	def _get_currency_position(self, data):
		config_id = self.env['dynamic.cheque.format.configuration'].browse([data.get('cheque_format_id')[0]])
		if config_id and config_id.currency_symbol and config_id.currency_symbol_position:
			return config_id.currency_symbol_position

	def _get_signatory_one(self, data):
		cheque_format_id = self.env['dynamic.cheque.format.configuration'].browse(data['form'].get('cheque_format_id')[0])
		return [cheque_format_id.first_signatory or '', cheque_format_id.second_signatory or '',
				cheque_format_id.third_signatory or '']

	def _get_company(self, data):
		cheque_format_id = self.env['dynamic.cheque.format.configuration'].browse(data['form'].get('cheque_format_id')[0])
		if cheque_format_id.company_name:
			return self.env['res.users'].browse([self._uid]).company_id.name

	def _draw_style(self, data, field):
		config_id = False
		style = ''
		if data.get('cheque_format_id'):
			config_id = self.env['dynamic.cheque.format.configuration'].browse([data.get('cheque_format_id')[0]])
		if config_id:
			if field == 'ac_pay':
				style = 'position:absolute;font-size:' + str(config_id.font_size_ac_pay) + 'mm;top:' + str(
					config_id.ac_pay_top_margin) + 'mm;left:' + str(
					config_id.ac_pay_left_margin) + 'mm;border-top:1px solid;border-bottom:1px solid;'
			elif field == 'payee_name':
				style = 'position:absolute;font-size:' + str(config_id.font_size_party_name) + 'mm;top:' + str(
					config_id.party_name_top_margin) + 'mm;left:' + str(
					config_id.party_name_left_margin) + 'mm;width:' + str(config_id.party_name_width_area) + 'mm;'
			elif field == 'cheque_date':
				style = 'position:absolute;font-size:' + str(config_id.font_size_cheque_date) + 'mm;margin-top:' + str(
					config_id.cheque_date_top_margin) + 'mm;margin-left:' + str(
					config_id.cheque_date_left_margin) + 'mm;letter-spacing:' + str(
					config_id.cheque_date_spacing) + 'mm;'
			elif field == 'first_amt_words':
				style = 'position:absolute;font-size:' + str(config_id.font_size_amt_word) + 'mm;width:' + str(
					config_id.amt_first_word_width_area) + 'mm;top:' + str(
					config_id.amt_word_first_line_top_margin) + 'mm;left:' + str(
					config_id.amt_word_first_line_left_margin) + 'mm;'
			elif field == 'second_amt_words':
				style = 'position:absolute;font-size:' + str(config_id.font_size_amt_word) + 'mm;width:' + str(
					config_id.amt_second_word_width_area) + 'mm;top:' + str(
					config_id.amt_word_second_line_top_margin) + 'mm;left:' + str(
					config_id.amt_word_second_line_left_margin) + 'mm;'
			elif field == 'amt_figure':
				style = 'position:absolute;font-size:' + str(config_id.font_size_amt_figure) + 'mm;top:' + str(
					config_id.amt_figure_top_margin) + 'mm;left:' + str(
					config_id.amt_figure_left_margin) + 'mm;width:' + str(config_id.amt_figure_width_area) + 'mm;'
			elif field == 'signatory_box':
				style = 'position:absolute;top:' + str(config_id.cmp_signatory_top_margin) + 'mm;left:' + str(
					config_id.cmp_signatory_left_margin) + 'mm;width:' + str(
					config_id.cmp_signatory_width) + 'mm;height:' + str(config_id.cmp_signatory_height) + 'mm;'
			elif field == 'company_name':
				style = 'position:absolute;font-size:' + str(config_id.font_size_company_name) + 'mm;top:' + str(
					config_id.company_name_top_margin) + 'mm;left:' + str(config_id.company_name_left_margin) + 'mm;'
			elif field == 'first_sign':
				style = 'position:absolute;font-size:' + str(config_id.font_size_first_signatory) + 'mm;top:' + str(
					config_id.first_signatory_top_margin) + 'mm;left:' + str(
					config_id.first_signatory_left_margin) + 'mm;'
			elif field == 'second_sign':
				style = 'position:absolute;font-size:' + str(config_id.font_size_second_signatory) + 'mm;top:' + str(
					config_id.second_signatory_top_margin) + 'mm;left:' + str(
					config_id.second_signatory_left_margin) + 'mm;'
			elif field == 'third_sign':
				style = 'position:absolute;font-size:' + str(config_id.font_size_third_signatory) + 'mm;top:' + str(
					config_id.third_signatory_top_margin) + 'mm;left:' + str(
					config_id.third_signatory_left_margin) + 'mm;'
		return style

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
