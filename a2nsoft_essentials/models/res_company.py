# -*- coding: utf-8 -*-
from odoo import models, fields , api


class res_company(models.Model):
    _inherit = 'res.company'
    
    
    inv_company = fields.Boolean("Is Inventoried")
