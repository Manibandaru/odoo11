# -*- coding: utf-8 -*-
from odoo import models, fields , api
import datetime
import dateutil

class HrOvertime(models.Model):
	_name = 'hr.overtime'


	employee_id = fields.Many2one('hr.employee','Employee')
	start_time = fields.Datetime('Start Time')
	end_time= fields.Datetime('End Time')
	total_hours = fields.Float('Total Hours', compute='total_ot_time')
	states = fields.Selection([('draft','Draft'),
							   ('approved','Approved'),
							   ('rejected','Rejected')
							   ],default='draft')
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)




	@api.multi
	def total_ot_time(self):
		for record in self:
			if record.start_time and record.end_time:
				start = datetime.datetime.strptime(record.start_time,"%Y-%m-%d %H:%M:%S")
				end = datetime.datetime.strptime(record.end_time,"%Y-%m-%d %H:%M:%S")
				print("*********************",(end-start))
				total_hours = end - start
				sec = total_hours.total_seconds()
				min = sec/60
				hrs = min/60
				record.total_hours = hrs



	@api.multi
	def approve_ot(self):
		for record in self:
			print(record.states)
			if record.states=='draft':
				record.states='approved'


	@api.multi
	def reject_ot(self):
		for record in self:
			print (record.states)
			if record.states=='draft':
				record.states='rejected'





##############################################
# UPDATE THE CONTRACT WITH EMPLOYEE HOURLY CHARGE

class HrContract(models.Model):
    _inherit = 'hr.contract'


    hourly_charge = fields.Float('OT Charge Per/Hour')


##################################################
# Calculate the total hours of the employee in the payslip for that month

class HrPayslipCustom(models.Model):
    _inherit = 'hr.payslip'


    total_ot_hours = fields.Float('Total OT Hours', compute='calculate_ot')


    def calculate_ot(self):
        for record in self:
            print(record.employee_id)

            ot_object = self.env['hr.overtime'].search([('employee_id','=',record.employee_id.id),
                                                        ('start_time','>=',record.date_from),
                                                        ('end_time','<=',record.date_to) ,
                                                        ('states','=','approved')
                                                        ])
            hours = 0
            for record in ot_object:
                hours = hours+ record.total_hours

            print("SUM HOURS",hours)
            self.total_ot_hours = hours







