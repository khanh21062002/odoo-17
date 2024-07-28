from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class LibraryTeacher(models.Model):
    _name = 'library.teacher'
    _description = 'Library Teacher'
    _inherit = 'mail.thread'

    name = fields.Char(string='Tên giáo viên', required=True, tracking=True)
    teacher_code = fields.Char(string='Mã giáo viên', default = lambda self:_('Giáo viên mới'))
    institute_id = fields.Many2one('library.institute', string="Khoa/Viện")
    level_id = fields.Many2one('library.level', string="Trình độ học vấn")
    gender = fields.Selection([('male', 'Nam'), ('female', 'Nữ')], string='Giới tính', required=True, tracking=True)
    birth_date = fields.Date(string='Ngày sinh', required=True, tracking=True)
    # age = fields.Integer(string='Tuổi', compute='_compute_age')
    address = fields.Text(string='Địa chỉ', required=True, tracking=True)
    phone_number = fields.Char(string='Số điện thoại', required=True, tracking=True)
    email = fields.Char(string='Email', required=True, tracking=True)
    note = fields.Text(string='Ghi chú')
    image = fields.Binary(string='Ảnh đại diện')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['teacher_code'] = self.env['ir.sequence'].next_by_code('library.teacher')
        return super(LibraryTeacher, self).create(vals_list)

    # @api.depends('birth_date')
    # def _compute_age(self):
    #     for teacher in self:
    #         if teacher.birth_date:
    #             today = fields.Date.today()
    #             age = today.year - teacher.birth_date.year - ((today.month, today.day) < (teacher.birth_date.month, teacher.birth_date.day))
    #             teacher.age = age
    #
    # @api.constrains('age')
    # def _check_age(self):
    #     for teacher in self:
    #         if teacher.age < 22:
    #             raise ValidationError(f"Giáo viên {teacher.name} phải trên 22 tuổi")
    #         if teacher.age > 80:
    #             raise ValidationError(f"Giáo viên {teacher.name} phải dưới 80 tuổi")






