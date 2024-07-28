from datetime import date
import re
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class LibraryStudent(models.Model):
    _name = 'library.student'
    _inherit = ['mail.thread']
    _description = 'Library Student'
    _order = 'name'
    _sql_constraints = [
        ('student_id_unique', 'unique(student_id)', "Mã sinh viên phải duy nhất !"),
    ]

    # Các thuộc tính cơ bản của sinh viên
    name = fields.Char(string='Tên sinh viên', required=True, tracking=True, size=255)
    student_id = fields.Char(string='Mã sinh viên ', default = lambda self:_('Sinh viên mới'))
    institute_id = fields.Many2one('library.institute', string="Khoa/Viện")
    level_id = fields.Many2one('library.level', string="Trình độ học vấn")
    birthday = fields.Date(string='Ngày sinh', required=True, tracking=True)
    age = fields.Integer(string='Tuổi', compute='_compute_age', inverse='_inverse_age')
    address = fields.Text(string='Địa chỉ', required=True, tracking=True)
    phone_number = fields.Char(string='Số điện thoại', required=True, tracking=True, size=15, index=True)
    email = fields.Char(string='Email', required=True, tracking=True, size=255, index=True)
    gender = fields.Selection([('male', 'Nam'), ('female', 'Nữ'), ('other', 'Khác')], string='Giới tính', required=True, tracking=True)
    note = fields.Text(string='Ghi chú')
    image = fields.Binary(string='Ảnh đại diện')

    # Các phương thức của quan lý sinh viên
    @api.constrains('birthday')
    def _check_date_of_birth(self):
        for r in self:
            if r.birthday > fields.Date.today():
                raise ValidationError(_('Ngày tháng năm sinh phải trong quá khứ.'))

    @api.depends('birthday')
    def _compute_age(self):
        curent_year = fields.Date.today().year
        for r in self:
            if r.birthday:
                r.age = curent_year - r.birthday.year
            else:
                r.age = 0
    def _inverse_age(self):
        for r in self:
            if r.age and r.birthday:
                curent_year = fields.Date.today().year
                dob_year = curent_year - r.age
                dob_month = r.birthday.month
                dob_day = r.birthday.day
                date_of_birth = date(dob_year, dob_month, dob_day)
                r.birthday = date_of_birth

    @api.constrains('age')
    def _check_age(self):
        for r in self:
            if r.age < 18:
                raise ValidationError(_('Tuổi của sinh viên phải trên 18 tuổi'))

    def check_number_format(self, str):
        regex = r'^[0-9]+$'
        if re.match(regex, str):
            return True
        else:
            return False

    def check_phone_number_format(self, str):
        valid = True
        if not str:
            valid = False
        else:
            if not self.check_number_format(str) or str[0] != '0' or len(str) != 10:
                valid = False
        return valid

    def check_email_format(self, str):
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(regex, str):
            return False
        vals = str.split('@')
        if len(vals[0]) < 5 or len(vals[0]) > 32:
            return False
        return True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['student_id'] = self.env['ir.sequence'].next_by_code('library.student')
        return super(LibraryStudent, self).create(vals_list)


