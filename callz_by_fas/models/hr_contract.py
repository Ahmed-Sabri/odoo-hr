# -*- coding: utf-8 -*-
#############################################################################
# Author: Fasil
# Email: fasilwdr@hotmail.com
# WhatsApp: https://wa.me/966538952934
# Facebook: https://www.facebook.com/fasilwdr
# Instagram: https://www.instagram.com/fasilwdr
#############################################################################

from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    daily_wage = fields.Monetary('Daily Wage', required=True, tracking=True, help="Employee's daily gross wage.")