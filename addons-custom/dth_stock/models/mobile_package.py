from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MobilePackage(models.Model):
    _name = 'dth.kho.mobile.package'
    _inherit = ['mail.thread']
    _description = 'Gói cước'

    name = fields.Char(string='Tên gói cước', required=True, tracking=True, size=50)
    code = fields.Char(string='Mã gói cước', required=True, index=True, tracking=True, size=50)
    telecom_supplier_id = fields.Many2one('dth.kho.telecom.supplier', string='Nhà mạng', required=True, index=True, tracking=True, ondelete='restrict')
    monthly_fee = fields.Char(string='Cước tháng', required=True, tracking=True)
    condition = fields.Text(string='Điều kiện áp dụng')
    endown_ids = fields.One2many('dth.kho.package.endown', 'package_id', string='Ưu đãi')
    note = fields.Text(string='Ghi chú')
    hot_endown = fields.Text(string='Ưu đãi nổi bật', compute='_compute_hot_endown', store=True)
    date_create = fields.Date(string='Ngày tạo', compute='_compute_date_create', store=True)
    date_update = fields.Date(string='Cập nhật', compute='_compute_date_update', store=True)
    active = fields.Boolean(default=True)
    
    @api.constrains('code', 'telecom_supplier_id')
    def _check_code(self):
        for r in self:
            if r.code and r.telecom_supplier_id:
                dupplicate = self.env['dth.kho.mobile.package'].search([('code', '=', r.code), 
                                                                ('telecom_supplier_id', '=', r.telecom_supplier_id.id),
                                                                ('id', '!=', r.id)], limit=1)
                if dupplicate:
                    raise ValidationError("Nhà mạng %s đã tồn tại gói cước có mã là '%s' rồi." % (r.telecom_supplier_id.name, r.code))
                
                
    @api.constrains('note')
    def _check_note(self):
        for r in self:
            if r.note and len(r.note) > 255:
                raise ValidationError("Ghi chú phải có độ dài không quá 255 ký tự.")
    
    @api.constrains('condition')
    def _check_condition(self):
        for r in self:
            if r.condition and len(r.condition) > 255:
                raise ValidationError("Điều kiện áp dụng phải có độ dài không quá 255 ký tự.")
    
    @api.depends('create_date')
    def _compute_date_create(self):
        for r in self:
            r.date_create = r.create_date.date()
    
    @api.depends('write_date')
    def _compute_date_update(self):
        for r in self:
            r.date_update = r.write_date.date()
    
    @api.depends('endown_ids.hot')
    def _compute_hot_endown(self):
        for r in self:
            r.hot_endown = ''
            if r.endown_ids:
                hot_endowns = r.endown_ids.filtered(lambda e: e.hot and e.is_active)
                if hot_endowns:
                    r.hot_endown = '\n'.join(hot_endowns.mapped('description'))
