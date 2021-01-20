# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2009-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: fasluca(<https://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
from psycopg2 import IntegrityError

from odoo.addons.mrp.models.mrp_production import MrpProduction as mp


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('planned', 'Planned'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',
        copy=False, default='draft', track_visibility='onchange')

    @api.model_cr
    def init(self):
        self.env.cr.execute('ALTER TABLE mrp_production DROP CONSTRAINT IF EXISTS mrp_production_name_uniq')
        self.env.cr.execute(
            '''CREATE UNIQUE INDEX IF NOT EXISTS mrp_mo_unique ON mrp_production (name,company_id) WHERE (state != 'draft')''')

    @api.model
    def create(self, values):
        production = super(mp, self).create(values)
        return production

    @api.multi
    def write(self, vals):
        try:
            res = super(MrpProduction, self).write(vals)
        except IntegrityError:
            raise ValidationError(_("Reference must be unique per Company for confirmed orders!"))
        if 'date_planned_start' in vals:
            moves = (self.mapped('move_raw_ids') + self.mapped('move_finished_ids')).filtered(
                lambda r: r.state not in ['done', 'cancel'])
            moves.write({
                'date_expected': vals['date_planned_start'],
            })
        if res:
            return res

    @api.multi
    def unlink(self):
        if any(production.state not in ['draft', 'cancel'] for production in self):
            raise UserError(_('Cannot delete a manufacturing order not in draft or cancel state'))
        return super(mp, self).unlink()

    @api.multi
    def action_confirm(self):
        if not self.name or self.name == _('New'):
            self.name = self.env['ir.sequence'].next_by_code('mrp.production') or _('New')
        if not self.procurement_group_id:
            self.procurement_group_id = self.env["procurement.group"].create({'name': self.name}).id
        self.state = 'confirmed'
        self._generate_moves()

