from odoo import models, fields, api

class InstallmentPeriod(models.Model):
    _name = 'dth.kho.installment.period'
    _description = 'Kỳ hạn trả góp'
    _order = 'id'

    name = fields.Char(string='Kỳ hạn')
