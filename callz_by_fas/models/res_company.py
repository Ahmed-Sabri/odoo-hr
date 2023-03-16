# -*- coding: utf-8 -*-
#############################################################################
# Author: Fasil
# Email: fasilwdr@hotmail.com
# WhatsApp: https://wa.me/966538952934
# Facebook: https://www.facebook.com/fasilwdr
# Instagram: https://www.instagram.com/fasilwdr
#############################################################################

from odoo import models, fields, api, _
import psycopg2
import logging

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = 'res.company'

    # Biotime Sync
    biotime_enable = fields.Boolean('Enable Biotime Sync', default=False)
    biotime_database = fields.Char('Database')
    biotime_host_address = fields.Char('Host Address')
    biotime_port = fields.Char('Port')
    biotime_user_id = fields.Char('User ID')
    biotime_password = fields.Char('User Password')


    def test_biotime_connection(self):
        try:
            conn = psycopg2.connect(
                database=self.env.company.biotime_database, user=self.env.company.biotime_user_id,
                password=self.env.company.biotime_password, host=self.env.company.biotime_host_address,
                port=self.env.company.biotime_port
            )
            if conn:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Connection Successful !!"),
                        'message': _("Go Ahead !"),
                        'type': 'success',
                        'sticky': False,
                    }
                }

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Connection Failed !!"),
                    'message': _("Error : %s" %(e)),
                    'type': 'warning',
                    'sticky': False,
                }
            }

    def cron_biotime_attendance_sync(self):
        self.sync_biotime_attendance()
        model = self.env['attendance.log']
        model.transfer_logs_day_first_in_out()

    def sync_biotime_attendance(self):
        if self.env.company.biotime_enable:
            result = []
            try:
                conn = psycopg2.connect(
                    database=self.env.company.biotime_database, user=self.env.company.biotime_user_id, password=self.env.company.biotime_password, host=self.env.company.biotime_host_address, port=self.env.company.biotime_port
                )
                conn.autocommit = True
                cursor = conn.cursor()
                last_id = self.env['attendance.log'].search([], limit=1, order='att_id desc')
                if last_id:
                    cursor.execute(
                        f'''SELECT id, emp_code,timezone('UTC', punch_time) AS punch_time, punch_state, verify_type,terminal_alias FROM public.iclock_transaction where ID > {last_id.att_id} ORDER BY punch_time DESC''')
                else:
                    cursor.execute(
                        '''SELECT id, emp_code,timezone('UTC', punch_time) AS punch_time, punch_state, verify_type,terminal_alias FROM public.iclock_transaction ORDER BY punch_time DESC''')
                result = cursor.fetchall()
                result.sort()
                result = list(result)
                conn.commit()
                conn.close()
            except Exception as e:
                _logger.warning("Error!!!!!! - ", e)
            if result:
                model = self.env['attendance.log']
                for rec in result:
                    record = model.search([('att_id', '=', rec[0])])
                    if not record:
                        model.create({
                            'att_id': rec[0],
                            'emp_code': rec[1],
                            'punch_time': rec[2],
                            'punch_state': rec[3],
                            'verify_type': rec[4],
                            'terminal_alias': rec[5],
                        })
        else:
            _logger.warning("Biotime Integration is not enabled..")

