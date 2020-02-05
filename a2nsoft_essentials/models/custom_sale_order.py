from odoo import models,api,fields



class cumtom_sales_order(models.Model):
    _inherit = 'sale.order'


    is_inventeriod = fields.Boolean('Is Inventoried')

    @api.model
    def default_get(self, fields):
        company_id = self.env.user.company_id

        rec = super(cumtom_sales_order, self).default_get(fields)
        if company_id.inv_company:
            rec.update({'is_inventeriod': True, })
        return rec