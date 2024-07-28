from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class LibraryComputer(models.Model):
    _name = 'library.computer'
    _description = 'Library Computer'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(string='Máy tính', required=True, tracking=True, size=255)
    computer_id = fields.Char(string='Mã máy tính', default = lambda self:_('Máy tính mới'), index=True)
    description = fields.Text(string='Mô tả', required=True, tracking=True)
    status = fields.Selection([('available', 'Có sẵn'), ('borrowed', 'Đã mượn'), ('maintenance', 'Bảo trì')], string='Trạng thái', required=True, tracking=True)
    note = fields.Text(string='Ghi chú')

    # @api.constrains('computer_id')
    # def _check_computer_id(self):
    #     for record in self:
    #         existing_record = self.search([('computer_id', '=', record.computer_id)], limit=1)
    #         if existing_record:
    #             raise ValidationError(_('Mã máy tính đã tồn tại.'))

    @api.constrains('status')
    def _check_status(self):
        for r in self:
            if r.status not in ['available', 'borrowed', 'maintenance']:
                raise ValidationError(_('Trạng thái phải là "Có sẵn", "Đã mượn" hoặc "Bảo trì".'))
            if r.status == 'maintenance' and not r.note:
                raise ValidationError(_('Nếu trạng thái là "Bảo trì", phải có ghi chú.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['computer_id'] = self.env['ir.sequence'].next_by_code('library.computer')
        return super(LibraryComputer, self).create(vals_list)