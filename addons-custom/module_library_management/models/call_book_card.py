from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class LibraryCallBookCard(models.Model):
    _name = 'library.call.book.card'
    _inherit = ['mail.thread']
    _description = 'Library Call Book Card'
    _order = 'book_id, borrow_date'

    code_call_book_card = fields.Char(string='Mã phiếu mượn sách', default = lambda self:_('Phiếu mượn sách mới'), index=True)
    book_id = fields.Many2many('library.book', string='Mã sách', index=True, tracking=True)
    is_student = fields.Boolean(string='Có phải là sinh viên không ?', default=False, required = True, tracking= True)
    student_id = fields.Many2one('library.student', string='Mã sinh viên', index=True, tracking=True)
    teacher_code = fields.Many2one('library.teacher', string='Mã giáo viên', index=True, tracking=True)
    borrow_date = fields.Date(string='Ngày mượn', default=fields.Datetime.today, required=True, tracking=True)
    due_date = fields.Date(string='Ngày trả', required=True, tracking=True)
    quality = fields.Integer(string='Số lượng mượn', required = True, tracking=True, default= 1)
    status_call_book_card = fields.Selection([('received', 'Còn hạn'), ('overdue', 'Quá hạn ')], string='Trạng thái phiếu mượn', default = 'received',compute = '_compute_status_call_book_card', store=True, tracking=True)
    note = fields.Text(string='Ghi chú')


    # @api.depends('borrow_date', 'book_id.due_date')
    # def _compute_due_date(self):
    #     for card in self:
    #         card.due_date = card.borrow_date + fields.Date.from_string(card.book_id.due_date)
    #
    # @api.depends('due_date')
    # def _compute_overdue_fee(self):
    #     for card in self:
    #         if card.due_date < fields.Date.today():
    #             card.overdue_fee = card.book_id.overdue_fee
    #
    # @api.constrains('book_id')
    # def _check_book_availability(self):
    #     for card in self:
    #         if card.book_id.available_quantity <= 0:
    #             raise ValidationError(f"Sách {card.book_id.name} đã hết")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['code_call_book_card'] = self.env['ir.sequence'].next_by_code('library.call.book.card')
        return super(LibraryCallBookCard, self).create(vals_list)

    @api.constrains('is_student','student_id','teacher_code')
    def _check_student_teacher(self):
        for r in self:
            if r.is_student == True and not r.student_id and r.teacher_code:
                raise ValidationError(_('Vui lòng chọn sinh viên. Không chọn giáo viên '))
            if r.is_student == False and not r.teacher_code and r.student_id:
                raise ValidationError(_('Vui lòng chọn giáo viên. Không chọn sinh viên '))
            if r.student_id and r.teacher_code:
                raise ValidationError(_('Vui lòng không chọn cả 2 '))

    @api.constrains('is_student','quality')
    def _check_quality(self):
        for r in self:
            if r.is_student == True and r.quality > 1:
                raise ValidationError(_('Sinh viên không thể mượn quá 1 cuốn sách'))
            if r.is_student == False and r.quality > 5:
                raise ValidationError(_('Giáo viên không thể mượn quá 5 cuốn sách'))

    @api.depends('borrow_date','due_date')
    def _compute_status_call_book_card(self):
        for card in self:
            if card.due_date >= fields.Date.today():
                card.status_call_book_card = 'received'
            else:
                card.status_call_book_card = 'overdue'





