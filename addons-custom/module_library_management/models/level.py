from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class LibraryLevel(models.Model):
    _name = 'library.level'
    _description = 'Library Level'
    _inherit = ['mail.thread']

    name = fields.Char(string='Trình độ học vấn ', required=True, tracking=True)
    level_code = fields.Char(string='Mã trình độ học vấn ', required=True, tracking=True)
    description = fields.Text(string='Mô tả', required=True, tracking=True)