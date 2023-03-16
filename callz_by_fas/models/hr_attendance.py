# -*- coding: utf-8 -*-
#############################################################################
# Author: Fasil
# Email: fasilwdr@hotmail.com
# WhatsApp: https://wa.me/966538952934
# Facebook: https://www.facebook.com/fasilwdr
# Instagram: https://www.instagram.com/fasilwdr
#############################################################################

from odoo import models, fields, api
from odoo.addons.resource.models.resource import float_to_time
from datetime import datetime
import pytz

DAYOFWEEK = {
    '0': 'Monday',
    '1': 'Tuesday',
    '2': 'Wednesday',
    '3': 'Thursday',
    '4': 'Friday',
    '5': 'Saturday',
    '6': 'Sunday'
}


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    late_arrival = fields.Float('Late Arrival', compute='_compute_late_early', store=True)
    early_leave = fields.Float('Early leave', compute='_compute_late_early', store=True)

    def new_timezone(self, time, format="%Y-%m-%d %H:%M:%S", user_tz=None):
        if not user_tz:
            user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        display_date_result = datetime.strftime(pytz.utc.localize(time, is_dst=0).astimezone(
            local), format)
        return display_date_result

    @api.depends('employee_id', 'check_in', 'check_out')
    def _compute_late_early(self):
        # attendances = self.env['hr.attendance'].search([])
        for att in self:
            late_arrival = 0
            early_leave = 0
            user_tz = att.employee_id.tz if att.employee_id.tz else None
            if att.check_in:
                check_in = datetime.strptime(att.new_timezone(time=att.check_in, user_tz=user_tz), '%Y-%m-%d %H:%M:%S')
                # print(check_in)
                if att.employee_id.resource_calendar_id:
                    dayofweek = check_in.strftime("%w")
                    hour_from = att.employee_id.resource_calendar_id.attendance_ids.filtered(lambda x: x.day_period == 'morning' and x.dayofweek == dayofweek).hour_from
                    if hour_from:
                        hour_from = float_to_time(hour_from)
                        hour_from_combine = datetime.combine(check_in.date(), hour_from)
                        # print(hour_from_combine)
                        if hour_from and check_in > hour_from_combine:
                            delta = check_in - hour_from_combine
                            late_arrival = (delta.total_seconds() / 60.0)
                            # print(late_arrival, "\n=======================")
            if att.check_out:
                check_out = datetime.strptime(att.new_timezone(time=att.check_out, user_tz=user_tz), '%Y-%m-%d %H:%M:%S')
                # print(check_out)
                if att.employee_id.resource_calendar_id:
                    dayofweek = check_out.strftime("%w")
                    hour_to = att.employee_id.resource_calendar_id.attendance_ids.filtered(lambda x: x.day_period == 'afternoon' and x.dayofweek == dayofweek).hour_to
                    if hour_to:
                        hour_to = float_to_time(hour_to)
                        hour_to_combine = datetime.combine(check_out.date(), hour_to)
                        if hour_to and check_out < hour_to_combine:
                            delta = hour_to_combine - check_out
                            early_leave = (delta.total_seconds() / 60.0)
                            # print(early_leave, "\n=======================")
            att.late_arrival = late_arrival
            att.early_leave = early_leave