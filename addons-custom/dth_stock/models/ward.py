# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Ward(models.Model):
    _name = 'res.country.ward'
    _description = 'Phường/xã'
    _order = 'code'

    district_id = fields.Many2one('res.country.district', string='Quận/huyện', required=True)
    active = fields.Boolean(default=True)
    name = fields.Char(string='Tên', required=True)
    code = fields.Char(string='Mã', required=True)
