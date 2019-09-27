# -*- coding: utf-8 -*-
from odoo import models, fields , api


class HrContract(models.Model):
    _inherit = 'hr.contract'



    hra_allowance = fields.Float('HRA')
    transport_alw = fields.Float('Transport Allowance')
    medical_allowance = fields.Float('Medical Allowance')
    food_allowance = fields.Float('Food Allowance')


class hr_payslip_run(models.Model):
	_inherit = 'hr.payslip.run'

	company_id = fields.Many2one('res.company',string='Company', default= lambda self:self.env.user.company_id.id)


class hr_holidays(models.Model):
	_inherit='hr.holidays'

	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)