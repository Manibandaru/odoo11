# -*- coding: utf-8 -*-
from odoo import models, fields , api


class HrContract(models.Model):
    _inherit = 'hr.contract'



    hra_allowance = fields.Float('HRA')
    transport_alw = fields.Float('Transport Allowance')

