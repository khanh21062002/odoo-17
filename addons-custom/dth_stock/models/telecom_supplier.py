from odoo import models, fields, api

class TelecomSupplier(models.Model):
    _name = 'dth.kho.telecom.supplier'
    _inherit = ['mail.thread', 'avatar.mixin']
    _description = 'Nhà mạng'
    _order = 'sequence asc'

    name = fields.Char(string='Tên nhà mạng', required=True, tracking=True)
    code = fields.Integer(string='Mã nhà mạng', required=True, tracking=True)
    image_128 = fields.Image("Logo", max_width=128, max_height=128)
    sequence = fields.Integer('Sequence', default=1)

    _sql_constraints = [
        ('telecom_supplier_unique_code', 'unique(code)', "Mã nhà mạng đã tồn tại")
    ]