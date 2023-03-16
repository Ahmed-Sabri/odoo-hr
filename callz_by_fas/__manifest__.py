# -*- coding: utf-8 -*-
{
    'name': 'Callz - Odoo Customization',
    'version': '16.0.1.0.4',
    'sequence': 0,
    'summary': """This module allows you to integrate Biotime attendance to Odoo""",
    'description': """"Integrate Biotime Attendance to Odoo
                    Attendance Integration Apps
                    Biotime Apps
                    First App for Biotime
                    Attendance Apps
                    Attendance Integration
                    ZK Attendance Apps
                    ZKteco Attendance Apps
                    """,
    'author': 'Fasil',
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': '99.99',
    'category': 'Tools',
    'company': 'Falgo Solutions',
    'website': "http://www.facebook.com/fasilwdr",
    'depends': ['base', 'hr_attendance', 'hr_payroll', 'hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_company.xml',
        'views/attendance_log.xml',
        'views/deduction_policy.xml',
        'views/hr_payslip.xml',
    ],
    'qweb': [],
    'images': [
        # 'static/description/banner.png'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
