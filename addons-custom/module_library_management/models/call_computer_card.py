from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class LibraryCallComputerCard(models.Model):
    _name = 'library.call.computer.card'
    _description = 'Library Call Computer Card'
    _inherit = ['mail.thread']

    code_call_computer_card = fields.Char(string='Mã phiếu mượn máy tính', default = lambda self:_('Phiếu mượn máy tính mới'), index=True)
    is_student = fields.Boolean(string='Có phải là sinh viên không ?', default=False, required = True, tracking= True)
    student_id = fields.Many2one('library.student', string='Mã sinh viên', index=True, tracking=True)
    teacher_code = fields.Many2one('library.teacher', string='Mã giáo viên', index=True, tracking=True)
    computer_id = fields.Many2one('library.computer', string='Mã máy tính', required=True, tracking=True)
    time_borrow = fields.Datetime(string='Giờ mượn',default=fields.Datetime.now, required=True, tracking=True)
    time_return = fields.Datetime(string='Giờ trả',required=True ,tracking=True)
    status_call_computer_card = fields.Selection([('received', 'Còn giờ'), ('overdue', 'Hết giờ')], string='Trạng thái phiếu mượn', default = 'received',compute = '_compute_status_call_computer_card', store=True, tracking=True)
    note = fields.Text(string='Ghi chú')

    # @api.constrains('time_borrow', 'time_return')
    # def _check_time_borrow_return(self):
    #     for r in self:
    #         if r.time_return and r.time_borrow and r.time_return < r.time_borrow:
    #             raise ValidationError("Gio trả phải l��n hơn hoặc b��ng gio mượn.")
    #         if r.time_return and r.time_borrow and r.time_return - r.time_borrow > fields.Date.today() - fields.Date.from_string('2022-01-01'):
    #             raise ValidationError("Khoảng th��i gian mượn quá hạn. Vui lòng kiểm tra lại th��i gian.")
    #         if not r.time_return and r.time_borrow and r.time_borrow < fields.Date.today():
    #             raise ValidationError("Gio mượn phải l��n hơn hoặc b��ng ngày hôm nay.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['code_call_computer_card'] = self.env['ir.sequence'].next_by_code('library.call.computer.card')
        return super(LibraryCallComputerCard, self).create(vals_list)

    @api.constrains('is_student','student_id','teacher_code')
    def _check_student_teacher(self):
        for r in self:
            if r.is_student == True and not r.student_id and r.teacher_code:
                raise ValidationError(_('Vui lòng chọn sinh viên. Không chọn giáo viên '))
            if r.is_student == False and not r.teacher_code and r.student_id:
                raise ValidationError(_('Vui lòng chọn giáo viên. Không chọn sinh viên '))
            if r.student_id and r.teacher_code:
                raise ValidationError(_('Vui lòng không chọn cả 2 '))

    @api.depends('time_borrow', 'time_return')
    def _compute_status_call_computer_card(self):
        for card in self:
            if card.time_return and card.time_return >= fields.Datetime.now():
                card.status_call_computer_card = 'received'
            else:
                card.status_call_computer_card = 'overdue'
