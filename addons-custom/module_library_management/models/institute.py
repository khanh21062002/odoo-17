from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class LibraryInstitute(models.Model):
    _name = 'library.institute'
    _description = 'Library Institute'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(string='Tên viện/khoa', required=True, tracking=True, size=255)
    code = fields.Char(string='Mã viện/khoa', required=True, tracking=True, index=True)
    description = fields.Text(string='Mô tả', required=True, tracking=True)

    # Các phương thức của quản lý viện/khoa
