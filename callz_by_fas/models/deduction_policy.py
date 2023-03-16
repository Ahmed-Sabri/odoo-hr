# -*- coding: utf-8 -*-
#############################################################################
# Author: Fasil
# Email: fasilwdr@hotmail.com
# WhatsApp: https://wa.me/966538952934
# Facebook: https://www.facebook.com/fasilwdr
# Instagram: https://www.instagram.com/fasilwdr
#############################################################################

from odoo import models, fields, api
from num2words import num2words


class DeductionPolicy(models.Model):
    _name = 'deduction.policy'
    _description = 'Deduction Policy'

    name = fields.Char('Description', compute='_compute_name')
    penalty = fields.Float('Penalty', required=True)
    late_early = fields.Integer('Late arrival/Early leave', required=True)
    repeat = fields.Integer('Repeatation', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)

    @api.onchange('penalty', 'late_early', 'repeat')
    def _compute_name(self):
        for i in self:
            i.write({
                'name': f"{i.penalty} days will be deducted if employee arrives late or leaves early by {i.late_early} minutes {num2words(i.repeat)} times in a month",
            })

    def unlink_policy(self):
        self.unlink()


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _get_deduction_policy(self):
        policy_ids = self.env['deduction.policy'].search([('company_id', '=', self.env.company.id)]).ids
        return policy_ids

    deduction_policy = fields.Many2many('deduction.policy', string='Deduction Policy', default=_get_deduction_policy)