# -*- coding: utf-8 -*-

from odoo import api, fields, models

class District(models.Model):
    _name = 'res.country.district'
    _description = 'Quận/huyện'
    _order = 'name'

    province_id = fields.Many2one('res.country.province', string='Tỉnh thành', required=True)
    active = fields.Boolean(default=True)
    name = fields.Char(string='Tên', required=True)
    code = fields.Char(string='Mã', required=True)
