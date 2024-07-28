from odoo import models, fields, api

class SimCategory(models.Model):
    _name = 'dth.kho.sim.category'
    _inherit = ['mail.thread']
    _description = 'Loại sim'
    _order = 'sequence asc'

    name = fields.Char(string='Tên loại sim', required=True, tracking=True)
    code = fields.Integer(string='Mã loại sim', required=True, tracking=True)
    sequence = fields.Integer(default=1)
    
    _sql_constraints = [
        ('sim_category_unique_code', 'unique(code)', "Mã loại sim đã tồn tại")
    ]
    
