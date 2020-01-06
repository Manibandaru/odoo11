# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class ReportTaxUae(models.AbstractModel):
	_name = 'report.vat_report.report_tax_uae'

	@api.model
	def get_report_values(self, docids, data=None):
		if not data.get('form'):
			raise UserError(_("Form content is missing, this report cannot be printed."))
		return {
			'data': data['form'],
			'lines': self.get_lines(data.get('form')),
		}

	def _sql_from_amls_one(self):
		sql = """SELECT "account_move_line".tax_line_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                    FROM %s
                    WHERE %s AND "account_move_line".tax_exigible GROUP BY "account_move_line".tax_line_id"""
		return sql

	def _sql_from_amls_two(self):
		sql = """SELECT r.account_tax_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                 FROM %s
                 INNER JOIN account_move_line_account_tax_rel r ON ("account_move_line".id = r.account_move_line_id)
                 INNER JOIN account_tax t ON (r.account_tax_id = t.id)
                 WHERE %s AND "account_move_line".tax_exigible GROUP BY r.account_tax_id"""
		return sql

	def _compute_from_amls(self, options, taxes):
		# compute the tax amount

		#
		# ####Sales
		# emirate_id = [547,546,548,549,550,551,552]
		#
		#
		# taxes_updated={}
		# vat = []
		# for em in emirate_id:
		# 	amls = " select SUM(aml.credit)- SUM(aml.debit) as net,SUM(aml.tax_base_amount) as base ,rs.name as emirate,at.name as tax,at.type_tax_use as type from account_move_line aml" \
		#        " LEFT JOIN res_country_state rs on aml.partner_state_id = rs.id  " \
		#        " LEFT JOIN account_tax at on aml.tax_line_id = at.id " \
		#        " where aml.tax_line_id is not NULL  AND at.type_tax_use='sale' AND aml.partner_state_id= " +str(em)  +" GROUP BY rs.name,at.name,at.type_tax_use"
		# 	self.env.cr.execute(amls)
		# 	results_vat = self.env.cr.dictfetchall()
		# 	if len(results_vat):
		# 		vat.append(results_vat[0])
		# #print("===========",vat)
		#
		# #non emirates
		# amls = " select SUM(aml.credit)- SUM(aml.debit) as net,SUM(aml.tax_base_amount) as base ,'others' as emirate,at.name as tax,at.type_tax_use as type from account_move_line aml" \
		#        " LEFT JOIN res_country_state rs on aml.partner_state_id = rs.id  " \
		#        " LEFT JOIN account_tax at on aml.tax_line_id = at.id " \
		#        " where aml.tax_line_id is not NULL AND aml.tax_exigible AND at.type_tax_use='sale' AND aml.partner_state_id  not in "+str(tuple(emirate_id))+"  GROUP BY rs.name,at.name,at.type_tax_use"
		# self.env.cr.execute(amls)
		# results_vat = self.env.cr.fetchall()
		# if len(results_vat):
		# 	vat.append(results_vat[0])
		# #print("vattttt",vat)
		#
		# taxes_updated['sale'] = vat
		# ######PURCHASE
		# pur_vat = []
		# for em in emirate_id:
		# 	amls = " select SUM(aml.debit)- SUM(aml.credit) as net,SUM(aml.tax_base_amount) as base ,rs.name as emirate,at.name as tax,at.type_tax_use as type from account_move_line aml" \
		# 	       " LEFT JOIN res_country_state rs on aml.partner_state_id = rs.id  " \
		# 	       " LEFT JOIN account_tax at on aml.tax_line_id = at.id " \
		# 	       " where aml.tax_line_id is not NULL AND aml.tax_exigible AND at.type_tax_use='purchase' AND aml.partner_state_id= " + str(
		# 		em) + " GROUP BY rs.name,at.name,at.type_tax_use"
		# 	self.env.cr.execute(amls)
		# 	results_vat = self.env.cr.fetchall()
		# 	if len(results_vat):
		# 		pur_vat.append(results_vat[0])
		# # print("===========",vat)
		#
		# # non emirates
		# amls = " select SUM(aml.debit)- SUM(aml.credit) as net,SUM(aml.tax_base_amount) as base ,'others' as emirate,at.name as tax,at.type_tax_use as type from account_move_line aml" \
		#        " LEFT JOIN res_country_state rs on aml.partner_state_id = rs.id  " \
		#        " LEFT JOIN account_tax at on aml.tax_line_id = at.id " \
		#        " where aml.tax_line_id is not NULL AND aml.tax_exigible AND at.type_tax_use='purchase' AND aml.partner_state_id  not in " + str(
		# 	tuple(emirate_id)) + "  GROUP BY rs.name,at.name,at.type_tax_use"
		# self.env.cr.execute(amls)
		# results_vat = self.env.cr.fetchall()
		# if len(results_vat):
		# 	pur_vat.append(results_vat[0])
		# #print("vattttt", pur_vat)
		# taxes_updated['purchase'] = pur_vat
		# print(taxes_updated)

		emirate_id = [547, 546, 548, 549, 550, 551, 552]
		line_dict={}

	##DUBAI
		dubai = " select SUM(aml.credit)- SUM(aml.debit) as net,SUM(aml.tax_base_amount) as base ,rs.name as emirate,at.name as tax,at.type_tax_use as type from account_move_line aml" \
		       " LEFT JOIN res_country_state rs on aml.partner_state_id = rs.id  " \
		       " LEFT JOIN account_tax at on aml.tax_line_id = at.id " \
		       " where aml.tax_line_id is not NULL  AND at.type_tax_use='sale' AND aml.partner_state_id='548' GROUP BY rs.name,at.name,at.type_tax_use"
		self.env.cr.execute(dubai)
		vat_dubai = self.env.cr.dictfetchall()
		#print("DUBAI==",vat_dubai)
		line_dict['Dubai'] = vat_dubai

	####sharjah
		sharjah = " select SUM(aml.credit)- SUM(aml.debit) as net,SUM(aml.tax_base_amount) as base ,rs.name as emirate,at.name as tax,at.type_tax_use as type from account_move_line aml" \
		        " LEFT JOIN res_country_state rs on aml.partner_state_id = rs.id  " \
		        " LEFT JOIN account_tax at on aml.tax_line_id = at.id " \
		        " where aml.tax_line_id is not NULL  AND at.type_tax_use='sale' AND aml.partner_state_id='551' GROUP BY rs.name,at.name,at.type_tax_use"
		self.env.cr.execute(sharjah)
		vat_shj = self.env.cr.dictfetchall()
		#print("SHARJAH==", vat_shj)
		line_dict['sharjah'] = vat_shj
	####Abu Dhabi
		abu_dhabi = " select SUM(aml.credit)- SUM(aml.debit) as net,SUM(aml.tax_base_amount) as base ,rs.name as emirate,at.name as tax,at.type_tax_use as type from account_move_line aml" \
		          " LEFT JOIN res_country_state rs on aml.partner_state_id = rs.id  " \
		          " LEFT JOIN account_tax at on aml.tax_line_id = at.id " \
		          " where aml.tax_line_id is not NULL  AND at.type_tax_use='sale' AND aml.partner_state_id='546' GROUP BY rs.name,at.name,at.type_tax_use"
		self.env.cr.execute(abu_dhabi)
		vat_abd = self.env.cr.dictfetchall()
		#print("ABU DHABI==", vat_abd)
		line_dict['abd'] = vat_abd

	#####FUJAIRAH
		fujairah = " select SUM(aml.credit)- SUM(aml.debit) as net,SUM(aml.tax_base_amount) as base ,rs.name as emirate,at.name as tax,at.type_tax_use as type from account_move_line aml" \
		            " LEFT JOIN res_country_state rs on aml.partner_state_id = rs.id  " \
		            " LEFT JOIN account_tax at on aml.tax_line_id = at.id " \
		            " where aml.tax_line_id is not NULL  AND at.type_tax_use='sale' AND aml.partner_state_id='549' GROUP BY rs.name,at.name,at.type_tax_use"
		self.env.cr.execute(fujairah)
		vat_fuj = self.env.cr.dictfetchall()
		#print("FUJAIRAh==", vat_fuj)
		line_dict['fuj'] = vat_fuj

	#########
		ajman = " select SUM(aml.credit)- SUM(aml.debit) as net,SUM(aml.tax_base_amount) as base ,rs.name as emirate,at.name as tax,at.type_tax_use as type from account_move_line aml" \
		           " LEFT JOIN res_country_state rs on aml.partner_state_id = rs.id  " \
		           " LEFT JOIN account_tax at on aml.tax_line_id = at.id " \
		           " where aml.tax_line_id is not NULL  AND at.type_tax_use='sale' AND aml.partner_state_id='547' GROUP BY rs.name,at.name,at.type_tax_use"
		self.env.cr.execute(ajman)
		vat_ajman = self.env.cr.dictfetchall()
		#print("ajman==", vat_ajman)
		line_dict['ajman'] = vat_ajman
	######RAS AL KAIMAH
		ras = " select SUM(aml.credit)- SUM(aml.debit) as net,SUM(aml.tax_base_amount) as base ,rs.name as emirate,at.name as tax,at.type_tax_use as type from account_move_line aml" \
		        " LEFT JOIN res_country_state rs on aml.partner_state_id = rs.id  " \
		        " LEFT JOIN account_tax at on aml.tax_line_id = at.id " \
		        " where aml.tax_line_id is not NULL  AND at.type_tax_use='sale' AND aml.partner_state_id='550' GROUP BY rs.name,at.name,at.type_tax_use"
		self.env.cr.execute(ras)
		vat_ras = self.env.cr.dictfetchall()
		#print("RAK==", vat_ras)
		line_dict['rak'] = vat_ras
	####UM AL QUWAIN
		umq =" select SUM(aml.credit)- SUM(aml.debit) as net,SUM(aml.tax_base_amount) as base ,rs.name as emirate,at.name as tax,at.type_tax_use as type from account_move_line aml" \
		        " LEFT JOIN res_country_state rs on aml.partner_state_id = rs.id  " \
		        " LEFT JOIN account_tax at on aml.tax_line_id = at.id " \
		        " where aml.tax_line_id is not NULL  AND at.type_tax_use='sale' AND aml.partner_state_id='550' GROUP BY rs.name,at.name,at.type_tax_use"
		self.env.cr.execute(umq)
		vat_umq = self.env.cr.dictfetchall()
		#print("UMQ==", vat_umq)
		line_dict['umq'] = vat_umq



		amls = " select SUM(aml.credit)- SUM(aml.debit) as net,SUM(aml.tax_base_amount) as base ,'others' as emirate,at.name as tax,at.type_tax_use as type from account_move_line aml" \
			       " LEFT JOIN res_country_state rs on aml.partner_state_id = rs.id  " \
	       " LEFT JOIN account_tax at on aml.tax_line_id = at.id " \
	       " where aml.tax_line_id is not NULL AND aml.tax_exigible AND at.type_tax_use='sale' AND aml.partner_state_id  not in "+str(tuple(emirate_id))+"  GROUP BY rs.name,at.name,at.type_tax_use"
		self.env.cr.execute(amls)
		vat_oth = self.env.cr.dictfetchall()
		# print("UMQ==", vat_umq)
		line_dict['others'] = vat_oth


		#########################################
		####PURCHASE
		pur_vat = " select SUM(aml.debit)- SUM(aml.credit) as net,SUM(aml.tax_base_amount) as base ,'purchase' as emirate,at.type_tax_use as type from account_move_line aml" \
		       " LEFT JOIN res_country_state rs on aml.partner_state_id = rs.id  " \
		       " LEFT JOIN account_tax at on aml.tax_line_id = at.id " \
		       " where aml.tax_line_id is not NULL AND aml.tax_exigible AND at.type_tax_use='purchase'  GROUP BY rs.name,at.type_tax_use"
		self.env.cr.execute(pur_vat)
		vat_pur = self.env.cr.dictfetchall()
		# print("UMQ==", vat_umq)
		line_dict['purchase'] = vat_pur

		print(line_dict)
		return line_dict

	@api.model
	def get_lines(self, options):
		taxes = {}
		for tax in self.env['account.tax'].search([('type_tax_use', '!=', 'none'),('company_id','=',self.env.user.company_id.id)]):
			if tax.children_tax_ids:
				for child in tax.children_tax_ids:
					if child.type_tax_use != 'none':
						continue
					taxes[child.id] = {'tax': 0, 'net': 0, 'name': child.name, 'type': tax.type_tax_use}
			else:
				taxes[tax.id] = {'tax': 0, 'net': 0, 'name': tax.name, 'type': tax.type_tax_use}

		groups = self.with_context(date_from=options['date_from'], date_to=options['date_to'],
		                  strict_range=True)._compute_from_amls(options, taxes)

		return groups
#
#
# # -*- coding: utf-8 -*-
#
# from odoo import api, models, _
# from odoo.exceptions import UserError
#
#
# class ReportTaxUae(models.AbstractModel):
# 	_name = 'report.vat_report.report_tax_uae'
#
# 	@api.model
# 	def get_report_values(self, docids, data=None):
# 		if not data.get('form'):
# 			raise UserError(_("Form content is missing, this report cannot be printed."))
# 		return {
# 			'data': data['form'],
# 			'lines': self.get_lines(data.get('form')),
# 		}
#
# 	def _sql_from_amls_one(self):
# 		sql = """SELECT "account_move_line".tax_line_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
#                     FROM %s
#                     WHERE %s AND "account_move_line".tax_exigible GROUP BY "account_move_line".tax_line_id"""
# 		return sql
#
# 	def _sql_from_amls_two(self):
# 		sql = """SELECT r.account_tax_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
#                  FROM %s
#                  INNER JOIN account_move_line_account_tax_rel r ON ("account_move_line".id = r.account_move_line_id)
#                  INNER JOIN account_tax t ON (r.account_tax_id = t.id)
#                  WHERE %s AND "account_move_line".tax_exigible GROUP BY r.account_tax_id"""
# 		return sql
#
# 	def _compute_from_amls(self, options, taxes):
#
#
# 		print(taxes)
# 		dxb = {'Dubai':taxes}
# 		query_dubai = """  select aml.tax_line_id ,COALESCE(SUM(aml.debit-aml.credit), 0)  from account_move_line aml
# 		        LEFT JOIN res_partner rp on aml.partner_id=rp.id
# 		        where aml.tax_line_id is not NULL AND aml.tax_exigible AND rp.state_id='548' GROUP BY aml.tax_line_id """
# 		self.env.cr.execute(query_dubai)
# 		results_vat = self.env.cr.fetchall()
# 		print(results_vat)
#
# 		for result in results_vat:
# 			if result[0] in dxb['Dubai']:
# 				dxb['Dubai'][result[0]]['tax'] = abs(result[1])
#
# 		print("Actual Taxes at DXB", taxes)
#
# 		shj = {'Sharjah':taxes}
# 		abd = {'Abu Dhabi': taxes}
# 		fjh = {'Al Fujairah' : taxes}
# 		rak = {'Ras Al kaimah': taxes}
# 		umq = {'Um Al quiwan':taxes}
# 		ajm = {'Ajman':taxes}
# 		###### DUBAI
#
#
# 		##### ABU DHABI
#
# 		query_adb = """  select aml.tax_line_id ,COALESCE(SUM(aml.debit-aml.credit), 0)  from account_move_line aml
# 		        LEFT JOIN res_partner rp on aml.partner_id=rp.id
# 		        where aml.tax_line_id is not NULL AND aml.tax_exigible AND rp.state_id='546' GROUP BY aml.tax_line_id """
# 		self.env.cr.execute(query_adb)
# 		results_vat = self.env.cr.fetchall()
# 		#print(results_vat)
# 		taxes_abd = abd
# 		for result in results_vat:
# 			if result[0] in abd['Abu Dhabi']:
# 				abd['Abu Dhabi'][result[0]]['tax'] = abs(result[1])
# 		#print("taxes_abd", abd)
#
#
#
#
# 	@api.model
# 	def get_lines(self, options):
# 		taxes = {}
# 		for tax in self.env['account.tax'].search([('type_tax_use', '!=', 'none')]):
# 			if tax.children_tax_ids:
# 				for child in tax.children_tax_ids:
# 					if child.type_tax_use != 'none':
# 						continue
# 					taxes[child.id] = {'tax': 0, 'net': 0, 'name': child.name, 'type': tax.type_tax_use}
# 			else:
# 				taxes[tax.id] = {'tax': 0, 'net': 0, 'name': tax.name, 'type': tax.type_tax_use}
#
# 		self.with_context(date_from=options['date_from'], date_to=options['date_to'],
# 		                  strict_range=True)._compute_from_amls(options, taxes)
# 		groups = dict((tp, []) for tp in ['sale', 'purchase'])
# 		for tax in taxes.values():
# 			if tax['tax']:
# 				groups[tax['type']].append(tax)
# 		return groups
