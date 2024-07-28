from odoo import models, fields, api

class PrepayAmount(models.Model):
    _name = 'dth.kho.prepay.amount'
    _description = 'Số tiền trả trước'
    _order = 'name'

    name = fields.Char(string='Phần trăm')
