from odoo import api, models,fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',required=1)
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',required=1)