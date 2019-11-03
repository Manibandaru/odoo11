

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class HrEmployeeDocument(models.Model):
    _name = 'hr.employee.document'
    _description = 'HR Employee Documents'

    def mail_reminder(self):
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        match = self.search([])
        for i in match:
            if i.expiry_date:
                exp_date = fields.Date.from_string(i.expiry_date) - timedelta(days=7)
                if date_now >= exp_date:
                    mail_content = "  Hello  " + i.employee_ref.name + ",<br>Your Document " + i.name + "is going to expire on " + \
                                   str(i.expiry_date) + ". Please renew it before expiry date"
                    main_content = {
                        'subject': _('Document-%s Expired On %s') % (i.name, i.expiry_date),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': i.employee_ref.work_email,
                    }
                    self.env['mail.mail'].create(main_content).send()

                    mail_content1 = "  Hello, Document " + i.name + " of one your employee (" + i.employee_ref.name + ")  " "is going to expire on " + \
                                   str(i.expiry_date) + ". Please renew it before expiry date"
                    main_content1 = {
	                    'subject': _('Document-%s Expired On %s') % (i.name, i.expiry_date),
	                    'author_id': self.env.user.partner_id.id,
	                    'body_html': mail_content1,
	                    'email_to': self.env.user.company_id.email,
                    }
                    self.env['mail.mail'].create(main_content1).send()

    @api.constrains('expiry_date')
    def check_expr_date(self):
        for each in self:
            exp_date = fields.Date.from_string(each.expiry_date)
            if exp_date < date.today():
                raise Warning('Your Document Is Expired.')

    @api.multi
    def compute_expiry(self):
        print("expiry dates==========")
        now = datetime.now()
        date_now = now.date()
        for record in self:
            if record.expiry_date:
                exp_date = fields.Date.from_string(record.expiry_date)
                print("expiry dates==========", (exp_date - date_now).days)
                record.days_expire = (exp_date - date_now).days
                expire_days = (exp_date - date_now).days

    @api.multi
    def compute_notify(self):
	    for record in self:
		    if record.days_expire and record.days_expire <= 30:
			    record.notify = True


    name = fields.Char(string='Document Number', required=True, copy=False)
    document_name = fields.Many2one('employee.checklist', string='Document', required=True)
    description = fields.Text(string='Description', copy=False)
    expiry_date = fields.Date(string='Expiry Date', copy=False)
    employee_ref = fields.Many2one('hr.employee', invisible=1, copy=False)
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel', 'doc_id', 'attach_id3', string="Attachment",
                                         help='You can attach the copy of your document', copy=False)
    issue_date = fields.Date(string='Issue Date', default=fields.datetime.now(), copy=False)
    days_expire = fields.Integer(string='Days to Expire', compute='compute_expiry')
    notify = fields.Boolean(string='Notify' , compute='compute_notify',store=True)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _document_count(self):
        for each in self:
            document_ids = self.env['hr.employee.document'].search([('employee_ref', '=', each.id)])
            each.document_count = len(document_ids)

    @api.multi
    def document_view(self):
        self.ensure_one()
        domain = [
            ('employee_ref', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'hr.employee.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Documents
                        </p>'''),
            'limit': 80,
            'context': "{'default_employee_ref': '%s'}" % self.id
        }

    document_count = fields.Integer(compute='_document_count', string='# Documents' ,store=True)


class HrEmployeeAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel = fields.Many2many('hr.employee.document', 'doc_attachment_id', 'attach_id3', 'doc_id',
                                      string="Attachment", invisible=1)
