# -*- coding: utf-8 -*-
#############################################################################
# Author: Fasil
# Email: fasilwdr@hotmail.com
# WhatsApp: https://wa.me/966538952934
# Facebook: https://www.facebook.com/fasilwdr
# Instagram: https://www.instagram.com/fasilwdr
#############################################################################

from odoo import models, fields
from datetime import datetime, timedelta, time
import logging

_logger = logging.getLogger(__name__)


class AttendanceLogs(models.Model):
    _name = 'attendance.log'
    _description = 'Attendance Logs'
    _order = 'punch_time desc'
    _rec_name = 'emp_code'

    att_id = fields.Integer('Biotime ID')
    emp_code = fields.Char('Employee Code')
    punch_time = fields.Datetime('Punch Time')
    punch_state = fields.Char('Punch Status')
    verify_type = fields.Integer('Verify Type')
    terminal_alias = fields.Char('Machine Name')
    transferred = fields.Boolean('Transferred')

    def transfer_logs_day_first_in_out(self):
        yesterday = datetime.combine(datetime.now(), time.max) - timedelta(days=1)
        no_punch_out_yday = self.env['hr.attendance'].search([('check_in', '<=', yesterday),('check_out', '=', False)])
        if no_punch_out_yday:
            for n in no_punch_out_yday:
                check_logs = self.env['attendance.log'].search([('emp_code', '=', n.employee_id.pin)], order='punch_time asc').filtered(lambda a: a.punch_time.date() == n.check_in.date())
                if check_logs:
                    n.check_out = check_logs[-1].punch_time
                    for l in check_logs:
                        l.transferred = True
        attendance_logs = self.env['attendance.log'].search([('transferred', '=', False), ('punch_time', '<=', yesterday)], order='punch_time asc')
        if attendance_logs:
            for log in attendance_logs:
                if not log.transferred:
                    employee = self.env['hr.employee'].search([('pin', '=', log.emp_code)], limit=1)
                    if employee:
                        new_logs = attendance_logs.filtered(lambda x: x.punch_time.date() == log.punch_time.date() and x.emp_code == employee.pin)
                        if len(new_logs) == 1:
                            self.env['hr.attendance'].create({
                                'employee_id': employee.id,
                                'check_in': new_logs.punch_time,
                                'check_out': new_logs.punch_time
                            })
                            new_logs.transferred = True
                        if len(new_logs) > 1:
                            self.env['hr.attendance'].create({
                                'employee_id': employee.id,
                                'check_in': new_logs[0].punch_time,
                                'check_out': new_logs[-1].punch_time
                            })
                            for x in new_logs:
                                x.transferred = True
                    else:
                        _logger.warning("Employee is not in system - " + log.emp_code)
        today = datetime.combine(datetime.now(), time.min)
        today_logs = self.env['attendance.log'].search([('punch_time', '>=', today), ('transferred', '=', False)], order='punch_time asc')
        if today_logs:
            for tl in today_logs:
                if not tl.transferred:
                    employee = self.env['hr.employee'].search([('pin', '=', tl.emp_code)], limit=1)
                    if employee:
                        check_logs = today_logs.filtered(lambda z: z.punch_time.date() == tl.punch_time.date() and z.emp_code == employee.pin)
                        check_in_today = self.env['hr.attendance'].search([('check_in', '>=', today), ('employee_id', '=', employee.id)], limit=1)
                        if check_in_today and check_logs:
                            check_in_today.check_out = check_logs[-1].punch_time
                        else:
                            self.env['hr.attendance'].create({
                                'employee_id': employee.id,
                                'check_in': check_logs[0].punch_time
                            })
                        for s in check_logs:
                            s.transferred = True
                    else:
                        _logger.warning("Employee is not in system - " + tl.emp_code)