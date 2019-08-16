import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class AccountMoveLine(models.Model):
	_inherit = "account.move.line"



	partner_state_id = fields.Many2one('res.country.state', related='partner_id.state_id', string='State',
	                                   readonly=True,store=True)
	partner_country_id = fields.Many2one('res.country', related='partner_id.country_id', string='Country',
	                                     readonly=True,store=True)