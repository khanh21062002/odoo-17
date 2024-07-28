# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Province(models.Model):
    _name = 'res.country.province'
    _description = 'Tỉnh thành'
    _order = 'name'

    country_id = fields.Many2one('res.country', string='Quốc gia', required=True)
    active = fields.Boolean(default=True)
    name = fields.Char(string='Tên', required=True)
    code = fields.Char(string='Mã', required=True)
