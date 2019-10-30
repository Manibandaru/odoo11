

from odoo import models, fields, api


class EmployeeEntryDocuments(models.Model):
    _name = 'employee.checklist'
    _inherit = 'mail.thread'
    _description = "Contact/Employee Documents"

    # @api.multi
    # def name_get(self):
    #     result = []
    #     for each in self:
    #         if each.document_type == 'entry':
    #             name = each.name + '_en'
    #         elif each.document_type == 'exit':
    #             name = each.name + '_ex'
    #         elif each.document_type == 'other':
    #             name = each.name + '_ot'
    #         result.append((each.id, name))
    #     return result

    name = fields.Char(string='Document Name', copy=False, required=1)
    document_type = fields.Selection([('entry', 'Entry Process'),
                                      ('exit', 'Exit Process'),
                                      ('renew','Renew'),
                                      ('other', 'Other')], string='Checklist Type', required=0)


