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

from openerp import fields, models, api, _
from openerp.exceptions import Warning
from datetime import datetime
import base64
#from wand.image import Image
import os, glob
import os.path


class dynamic_cheque_format_configuration(models.Model):
	_name = 'dynamic.cheque.format.configuration'

	@api.model
	def _get_report_paperformat_id(self):
		xml_id = self.env['ir.actions.report'].search([('report_name', '=',
															'dynamic_cheque_print.dynamic_cheque_print_template')])
		# if not xml_id or not xml_id.paperformat_id:
		# 	raise Warning('Someone has deleted the reference paperformat of report.Please Update the module!')
		return xml_id.paperformat_id.id

	paper_format_id = fields.Many2one('report.paperformat', string="Paper Format", default=_get_report_paperformat_id)
	name = fields.Char(string="Cheque Format")
	# cheque Height-Width Configuration
	cheque_height = fields.Float(string="Height", default=92)
	cheque_width = fields.Float(string="Width", default=199)
	# ac_pay Configuration
	is_ac_pay = fields.Boolean(string="A/c Pay", default=True)
	ac_pay_top_margin = fields.Float(string="Top Margin", default=15)
	ac_pay_left_margin = fields.Float(string="Left Margin", default=10)
	font_size_ac_pay = fields.Float(string="Font Size", default=3)
	# cheque Date Configuration
	cheque_date_top_margin = fields.Float(string="Top Margin", default=8)
	cheque_date_left_margin = fields.Float(string="Left Margin", default=150)
	font_size_cheque_date = fields.Float(string="Font Size", default=5)
	cheque_date_spacing = fields.Float(string="Character Spacing", default=2)
	# Party's/Payee Name Configuration
	party_name_top_margin = fields.Float(string="Top Margin", default=22)
	party_name_left_margin = fields.Float(string="Left Margin", default=13)
	party_name_width_area = fields.Float(string="Width", default=167)
	font_size_party_name = fields.Float(string="Font Size", default=4)
	# Amount in words Configuration
	font_size_amt_word = fields.Float(string="Font Size", default=4)
	amt_word_first_line_top_margin = fields.Float(string="First Line Top Margin", default=30)
	amt_word_first_line_left_margin = fields.Float(string="First Line Left Margin", default=25)
	amt_first_word_width_area = fields.Float(string="First Line Width", default=99)
	first_line_words_count = fields.Integer(string="No. of words in 1st line", default=25)
	amt_word_second_line_top_margin = fields.Float(string="Second Line Top Margin", default=36)
	amt_word_second_line_left_margin = fields.Float(string="Second Line Left Margin", default=15)
	amt_second_word_width_area = fields.Float(string="Second Line Width", default=99)
	second_line_words_count = fields.Integer(string="No. of words in 2nd line", default=25)
	currency_name = fields.Boolean(string="Currency Name", default=True)
	currency_name_position = fields.Selection([('before', 'Before'), ('after', 'After')],
											  string="Currency Name Position",
											  default='before')
	amount_word_type = fields.Selection([('standard', 'Standard'), ('capital', 'All Capital'), ('small', 'All Small')],
										default='standard', string="Amount in Word Type")
	# Amount in Figure Configuration
	font_size_amt_figure = fields.Float(string="Font Size", default=5)
	amt_figure_top_margin = fields.Float(string="Top Margin", default=34)
	amt_figure_left_margin = fields.Float(string="Left Margin", default=155)
	amt_figure_width_area = fields.Float(string="Width", default=41)
	currency_symbol = fields.Boolean(string="Currency Symbol", default=True)
	currency_symbol_position = fields.Selection([('before', 'Before'), ('after', 'After')],
												string="Currency Symbol Position",
												default='before')
	# Company Signatory Details
	company_name = fields.Boolean(string="Company Name", default=True)
	font_size_company_name = fields.Float(string="Font Size", default=4)
	company_name_top_margin = fields.Float(string="Top Margin", default=64)
	company_name_left_margin = fields.Float(string="Left Margin", default=147)
	# signator space
	cmp_signatory_width = fields.Float(string="Width", default=50)
	cmp_signatory_height = fields.Float(string="Height", default=10)
	cmp_signatory_top_margin = fields.Float(string="Top Margin", default=70)
	cmp_signatory_left_margin = fields.Float(string="Left Margin", default=147)
	# first signator
	font_size_first_signatory = fields.Float(string="Font Size", default=3)
	first_signatory = fields.Char(string="Salutation of 1st Signatory")
	first_signatory_top_margin = fields.Float(string="Top Margin", default=80)
	first_signatory_left_margin = fields.Float(string="Left Margin", default=127)
	# second signator
	font_size_second_signatory = fields.Float(string="Font Size", default=3)
	second_signatory = fields.Char(string="Salutation of 2nd Signatory")
	second_signatory_top_margin = fields.Float(string="Top Margin", default=80)
	second_signatory_left_margin = fields.Float(string="Left Margin", default=144)
	# third signator
	font_size_third_signatory = fields.Float(string="Font Size", default=3)
	third_signatory = fields.Char(string="Salutation of 3rd Signatory")
	third_signatory_top_margin = fields.Float(string="Top Margin", default=80)
	third_signatory_left_margin = fields.Float(string="Left Margin", default=170)


class wizard_cheque_preview(models.TransientModel):
	_name = 'wizard.cheque.preview'

	supplier_id = fields.Many2one("res.partner", string="Supplier Name")
	payment_date = fields.Date(string="Date")
	amount = fields.Float(string="Amount")
	currency_id = fields.Many2one("res.currency", string="Currency")
	image_preview = fields.Binary(string="Image")
	is_preview = fields.Boolean(string="Preview")

	@api.multi
	def action_cheque_preview(self):

		encoded_string = ''
		data = self.read()[0]
		cheque_config_id = self.env['dynamic.cheque.format.configuration'].browse(self._context.get('active_id'))
		if cheque_config_id:
			cheque_config_id.paper_format_id.write({
				'format': 'custom',
				'page_width': cheque_config_id.cheque_width,
				'page_height': cheque_config_id.cheque_height,
			})
		data.update({'label_preview': True, 'cheque_format_id': [cheque_config_id.id, cheque_config_id.name]})
		datas = {
			'ids': self.id,
			'model': 'wizard.cheque.preview',
			'form': data
		}
		pdf_data = self.env['report'].get_html(self, 'check_printing.dynamic_cheque_print_template', data=datas)
		body = [(self.id, pdf_data)]
		pdf_image = self.env['report']._run_wkhtmltopdf([], [], body, None, cheque_config_id.paper_format_id,
														{}, {'loaded_documents': {}, 'model': u'account.payment'})
		with Image(blob=pdf_image) as img:
			filelist = glob.glob("/tmp/*.jpg")
			for f in filelist:
				os.remove(f)
			img.save(filename="/tmp/temp.jpg")
		if os.path.exists("/tmp/temp-0.jpg"):
			with open(("/tmp/temp-0.jpg"), "rb") as image_file:
				encoded_string = base64.b64encode(image_file.read())
		elif os.path.exists("/tmp/temp.jpg"):
			with open(("/tmp/temp.jpg"), "rb") as image_file:
				encoded_string = base64.b64encode(image_file.read())
		self.write({'image_preview': encoded_string, 'is_preview': True})
		ctx = self._context
		return {
			'name': _('Cheque Preview'),
			'type': 'ir.actions.act_window',
			'view_mode': 'form',
			'res_model': 'wizard.cheque.preview',
			'target': 'new',
			'res_id': self.id,
			'context': ctx,
		}


class wizard_dynamic_cheque_print(models.TransientModel):
	_name = 'wizard.dynamic.cheque.print'

	cheque_format_id = fields.Many2one('dynamic.cheque.format.configuration', string="Cheque Format")

	@api.multi
	def action_call_report(self):
		data = self.read()[0]
		if self.cheque_format_id.paper_format_id and self.cheque_format_id.cheque_height <= 0 or self.cheque_format_id.cheque_width <= 0:
			raise Warning(_("Cheque height and width can not be less than Zero(0)."))

		result = self.cheque_format_id.paper_format_id.write({
			'format': 'custom',
			'page_width': self.cheque_format_id.cheque_width,
			'page_height': self.cheque_format_id.cheque_height,
		})


		datas = {
			'ids': self._context.get('active_id'),
			'model': 'wizard.dynamic.cheque.print',
			'form': data
		}
		#print("data=====================",datas)
		return self.env.ref('check_printing.dynamic_cheque_print_report').report_action(self, data=datas)



