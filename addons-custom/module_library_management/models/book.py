from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class LibraryBook(models.Model):
    _name = 'library.book'
    _inherit = ['mail.thread']
    _description = 'Library Book'

    name = fields.Char(string='Tên cuốn sách', required=True, tracking=True, size=255)
    language = fields.Selection([('en', 'Tiếng Anh'), ('ar', 'Tiếng Ả Rập'), ('fr', 'Tiếng Pháp'), ('es', 'Tiếng Tây Ban Nha'), ('de', 'Tiếng Đức'), ('vn', 'Tiếng Việt') ],
                                string='Ngôn ngữ')
    book_id = fields.Char(string='Mã sách ', default = lambda self:_('Sách mới'), index=True)
    author = fields.Char(string='Tác giả', required=True, tracking=True, size=255)
    publisher = fields.Char(string='Nhà xuất bản', required=True, tracking=True, size=255)
    publication_year = fields.Integer(string='Năm xuất bản', required=True, tracking=True)
    genre = fields.Selection([('fiction', 'Văn học'), ('nonfiction', 'Kinh tế'), ('detective', 'Trinh thám'), ('history', 'Lịch sử'), ('technique', 'Kỹ thuật')], string='Thể loại', required=True, tracking=True)
    status = fields.Selection([('available', 'Còn sách'), ('borrowed', 'Đã mượn')], string='Trạng thái', compute = '_compute_status',store=True, tracking=True)
    note = fields.Text(string='Ghi chú')
    quality = fields.Integer(string='Số lượng sách trong thư viện', default = 0, tracking=True)
    quality_borrow = fields.Integer(string='Số lượng sách đã mượn', default = 1, tracking=True)
    quality_remaining = fields.Integer(string='Số lượng sách còn lại ', compute='_compute_quality_remaining')
    people_list = fields.Many2many('library.call.book.card',string='Danh sách người mượn')

    @api.constrains('publication_year')
    def _check_publication_year(self):
        for r in self:
            if r.publication_year < 0:
                raise ValidationError(_('Năm xuất bản: Giá trị phải lớn hơn hoặc bằng 0.'))
            if r.publication_year > fields.Date.today().year:
                raise ValidationError(_('Năm xuất bản: Giá trị phải nh�� hơn hoặc b��ng năm hiện tại.'))

    @api.constrains('due_date')
    def _check_due_date(self):
        for r in self:
            if r.due_date < r.borrow_date:
                raise ValidationError(_('Hạn trả: Ngày hạn trả phải l��n hơn ngày mượn.'))
            if r.due_date < fields.Date.today():
                raise ValidationError(_('Hạn trả: Ngày hạn trả đã quá hạn.'))

    @api.constrains('quality')
    def _check_quality(self):
        for r in self:
            if r.quality < 0:
                raise ValidationError(_('Số lượng: Giá trị phải l��n hơn hoặc b��ng 0.'))

    @api.constrains('quality_borrow')
    def _check_quality_borrow(self):
        for r in self:
            if r.quality_borrow < 0:
                raise ValidationError(_('Số lượng đã mượn: Giá trị phải lớn hơn hoặc bằng 0.'))
            if r.quality_borrow > r.quality:
                raise ValidationError(_('Số lượng đã mượn: Giá trị phải nhỏ hơn hoặc bằng Số lượng sách trong thư viện.'))

    @api.depends('quality', 'quality_borrow')
    def _compute_quality_remaining(self):
        for r in self:
            if r.quality and r.quality_borrow or r.quality_remaining == 0:
                r.quality_remaining = r.quality - r.quality_borrow
            else:
                r.quality_remaining = 0

    @api.depends('quality_remaining')
    def _compute_status(self):
        for r in self:
            if r.quality_remaining == 0:
                r.status = 'borrowed'
            else:
                r.status = 'available'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['book_id'] = self.env['ir.sequence'].next_by_code('library.book')
        return super(LibraryBook, self).create(vals_list)