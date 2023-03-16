# -*- coding: utf-8 -*-
#############################################################################
# Author: Fasil
# Email: fasilwdr@hotmail.com
# WhatsApp: https://wa.me/966538952934
# Facebook: https://www.facebook.com/fasilwdr
# Instagram: https://www.instagram.com/fasilwdr
#############################################################################

from odoo import models, fields, api
from odoo import Command
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    late_early_attendance_ids = fields.Many2many('hr.attendance', string="Late Early Attendances")
    late_arrival_days = fields.Integer('Late Arrival Days')
    late_arrival_penalty = fields.Float('Late Arrival Penalty')
    early_leave_days = fields.Integer('Early Leave Days')
    early_leave_penalty = fields.Float('Early Arrival Penalty')
    late_early_deduction_total = fields.Monetary('Deduction Total', currency_field='currency_id', compute='_compute_late_early_deduction_total', store=True)

    @api.depends('late_arrival_penalty', 'early_leave_penalty')
    def _compute_late_early_deduction_total(self):
        for i in self:
            i.write({
                'late_early_deduction_total': i.late_arrival_penalty + i.early_leave_penalty
            })

    def prepare_late_early_inputs(self):
        ded_cat = self.env.ref('hr_payroll.input_deduction')
        if self.late_arrival_penalty > 0:
            late_deduction = self.input_line_ids.filtered(lambda i: i.name == 'Late Arrival Deduction')
            if not late_deduction:
                self.env['hr.payslip.input'].create({
                    'name': 'Late Arrival Deduction',
                    'payslip_id': self.id,
                    'sequence': 12,
                    'input_type_id': ded_cat.id,
                    'amount': self.late_arrival_penalty * self.contract_id.daily_wage
                })
            else:
                late_deduction.update({
                    'amount': self.late_arrival_penalty * self.contract_id.daily_wage
                })
        if self.early_leave_penalty > 0:
            early_deduction = self.input_line_ids.filtered(lambda i: i.name == 'Early Leave Deduction')
            if not early_deduction:
                self.env['hr.payslip.input'].create({
                    'name': 'Early Leave Deduction',
                    'payslip_id': self.id,
                    'sequence': 13,
                    'input_type_id': ded_cat.id,
                    'amount': self.early_leave_penalty * self.contract_id.daily_wage
                })
            else:
                early_deduction.update({
                    'amount': self.early_leave_penalty * self.contract_id.daily_wage
            })

    def compute_sheet(self):
        for payslip in self:
            penalty_policy = self.env['deduction.policy'].search(
                [('company_id', '=', payslip.employee_id.company_id.id)], order='penalty')
            print(penalty_policy)
            if penalty_policy:
                lowest = min([x.late_early for x in penalty_policy])
                count_list = list(set([x.repeat for x in penalty_policy]))
                attendances = self.env['hr.attendance'].search([
                    "&", ('employee_id', '=', payslip.employee_id.id),
                    "&", ('check_in', '>=', payslip.date_from),
                    "&", ('check_in', '<=', payslip.date_to),
                    "&", ('check_out', '!=', False),
                    '|',
                    ('late_arrival', '>=', lowest),
                    ('early_leave', '>=', lowest)
                ])
                if attendances:
                    late = attendances.filtered(lambda z: z.late_arrival > lowest)
                    late_arrival_days = len(late)
                    for att1 in late:
                        print(att1.late_arrival, "late_arrival")
                    early = attendances.filtered(lambda z: z.early_leave > lowest)
                    early_leave_days = len(early)
                    for att2 in early:
                        print(att2.early_leave, "early_leave")
                    late_arrival_penalty = early_leave_penalty = 0
                    late_penalty = []
                    early_penalty = []
                    if late_arrival_days > 0:
                        for count in count_list:
                            temp_list = penalty_policy.filtered(lambda x: x.repeat == count)
                            for i in range(len(temp_list)):
                                late_new = late.filtered(lambda x: x.late_arrival >= temp_list[i].late_early)
                                if late_new and i != (len(temp_list)-1):
                                    late_new = late_new.filtered(lambda x: x.late_arrival < temp_list[i + 1].late_early)
                                if count == len(late_new):
                                    late_penalty.append(temp_list[i].penalty)
                        if late_penalty:
                            late_arrival_penalty = max(late_penalty)
                        late_arrival_penalty += (late_arrival_days - 1)
                    if early_leave_days > 0:
                        for count in count_list:
                            temp_list = penalty_policy.filtered(lambda x: x.repeat == count)
                            for i in range(len(temp_list)):
                                late_new = early.filtered(lambda x: x.early_leave >= temp_list[i].late_early)
                                if late_new and i != (len(temp_list) - 1):
                                    late_new = late_new.filtered(
                                        lambda x: x.early_leave < temp_list[i + 1].late_early)
                                if count == len(late_new):
                                    early_penalty.append(temp_list[i].penalty)
                        if early_penalty:
                            early_leave_penalty = max(early_penalty)
                        early_leave_penalty += (early_leave_days - 1)
                    self.write({
                        'late_early_attendance_ids': [Command.set(attendances.ids)],
                        'late_arrival_days': late_arrival_days,
                        'late_arrival_penalty': late_arrival_penalty,
                        'early_leave_days': early_leave_days,
                        'early_leave_penalty': early_leave_penalty,
                    })
                    payslip.prepare_late_early_inputs()
            else:
                raise UserError("Please set the attendance penalty policy in the settings.")
        return super().compute_sheet()
