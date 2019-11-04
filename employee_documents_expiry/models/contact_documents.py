

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning



class contact_documents(models.Model):
	_name = 'contact.document'

	def mail_reminder(self):
		now = datetime.now() + timedelta(days=1)
		date_now = now.date()
		match = self.search([])
		for i in match:
			if i.expiry_date:
				exp_date = fields.Date.from_string(i.expiry_date) - timedelta(days=7)
				if date_now >= exp_date:
					mail_content = "  Hello, Your Document  " + i.name + "is going to expire on " + \
					               str(i.expiry_date) + ". Please renew it before expiry date"
					main_content = {
						'subject': _('Document-%s Expired On %s') % (i.name, i.expiry_date),
						'author_id': self.env.user.partner_id.id,
						'body_html': mail_content,
						'email_to': i.document_holder.email ,
					}
					self.env['mail.mail'].create(main_content).send()

					mail_content1 = "  Hello,The Document with reference number " + i.name +  ", of  Your Client " + i.document_holder.name + "   is going to expire on " + \
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
		now = datetime.now()
		date_now = now.date()
		for record in self:
			if record.expiry_date:
				exp_date = fields.Date.from_string(record.expiry_date)
				# print("expiry dates==========",(exp_date-date_now).days)
				record.days_expire = (exp_date-date_now).days
				expire_days = (exp_date - date_now).days


	@api.depends('days_expire')
	@api.multi
	def compute_notify(self):
		for record in self:
			if record.days_expire and record.days_expire <= 30 :
				record.notify = True




	name = fields.Char(string='Document Number', required=True, copy=False)
	document_name = fields.Many2one('employee.checklist', string='Document', required=True)
	description = fields.Text(string='Description', copy=False)
	expiry_date = fields.Date(string='Expiry Date', copy=False)
	doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel1', 'doc_id', 'attach_id3', string="Attachment",
	                                     help='You can attach the copy of your document', copy=False)
	issue_date = fields.Date(string='Issue Date', default=fields.datetime.now(), copy=False)

	document_holder = fields.Many2one('res.partner', string='Document Holder')
	company_name = fields.Many2one('res.partner',string='Company')
	days_expire = fields.Integer(string='Days to Expire',compute='compute_expiry' )
	notify = fields.Boolean(string='Notify' , compute='compute_notify' ,default=False ,store=True)
	company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env.user.company_id.id)




class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _document_count(self):
        for each in self:
            document_ids = self.env['contact.document'].search([('document_holder', '=', each.id)])
            each.document_count = len(document_ids)

    @api.multi
    def document_view(self):
        self.ensure_one()
        domain = [
            ('document_holder', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'contact.document',
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

    document_count = fields.Integer(compute='_document_count', string='# Documents', store=True)


class CustomerAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel1 = fields.Many2many('contact.document', 'doc_attachment_id', 'attach_id3', 'doc_id',
                                      string="Attachment", invisible=1)
