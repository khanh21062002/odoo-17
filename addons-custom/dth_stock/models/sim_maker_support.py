from odoo import models, fields, api
from odoo.tools import float_is_zero
from odoo.exceptions import UserError, ValidationError

class SimMakerSupport(models.Model):
    _name = 'dth.kho.sim.maker.support'
    _description = 'Hỗ trợ'
    _order = 'support_type,min_amount'

    sim_maker_id = fields.Many2one('dth.kho.sim.maker', string='Thợ sim', ondelete='cascade', index=True)
    support_type = fields.Selection([('phi_giao_sim', 'Phí giao sim'), 
                                     ('phi_sim_trang', 'Phí sim trắng'), 
                                     ('phi_cat_sim', 'Phí cắt sim')], string='Loại hỗ trợ', default='phi_giao_sim', required=True)
    
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', default=lambda self: self.env.ref('base.VND'))
    min_amount = fields.Monetary(string='Giá min', currency_field='currency_id', required=True)
    max_amount = fields.Monetary(string='Giá max', currency_field='currency_id', required=True)
    support_amount_type = fields.Selection([('percent', 'Phần trăm'), ('fix', 'Tiền')], default='percent', string='Kiểu giá trị', required=True)
    support_amount = fields.Monetary(string='Tiền hỗ trợ', currency_field='currency_id')
    support_percent = fields.Float(string='Phần trăm hỗ trợ')
    
    @api.constrains('support_amount_type', 'support_amount', 'support_percent')
    def _check_support_type(self):
        for r in self:
            if r.support_amount_type == 'percent':
                if r.support_percent <= 0 or r.support_percent > 100:
                    raise ValidationError("Đối với kiểu hỗ trợ theo 'Phần trăm' thì giá trị Phần trăm hỗ trợ phải nằm trong khoảng 1-100.")
            else:
                if r.support_amount <= 0:
                    raise ValidationError("Đối với kiểu hỗ trợ theo 'Tiền' thì giá trị Tiền hỗ trợ phải lớn hơn 0.")
    
    @api.constrains('min_amount', 'max_amount')
    def _constrains_amount(self):
        for r in self:
            if r.min_amount < 0 or r.max_amount < 0:
                raise ValidationError('Hỗ trợ: Giá min và giá max phải lớn hơn hoặc bằng 0.')
            if not float_is_zero(r.max_amount, precision_rounding=2) and r.min_amount >= r.max_amount:
                raise ValidationError('Hỗ trợ: Giá max phải lớn hơn giá min, nếu muốn để giá max là vô hạn, bạn đặt giá max về 0.')
            domain = []
            if not float_is_zero(r.max_amount, precision_rounding=2):
                domain = [('sim_maker_id', '=', r.sim_maker_id.id),
                          ('support_type', '=', r.support_type),
                         ('id', '!=', r.id),
                         '|', '&', '&',('max_amount', '>', 0),
                                ('min_amount', '<=', r.max_amount),
                                ('max_amount', '>=', r.min_amount),
                                '&', ('max_amount', '=', 0),
                                ('min_amount', '<=', r.max_amount)]
            else:
                domain = [('sim_maker_id', '=', r.sim_maker_id.id),
                          ('support_type', '=', r.support_type),
                         ('id', '!=', r.id),
                         '|', '&',('max_amount', '>', 0),
                                ('max_amount', '>=', r.min_amount),
                                ('max_amount', '=', 0)]
            overlap_supports = self.env['dth.kho.sim.maker.support'].search(domain, limit=1)
            if overlap_supports:
                raise ValidationError("Hỗ trợ: Đối với loại hỗ trợ '%s' khoảng giá vừa tạo (điều chỉnh) bị chồng lấn với khoảng giá từ %s đến %s đã tạo trước đó." % (dict(r._fields['support_type'].selection).get(r.support_type), overlap_supports[0].min_amount, overlap_supports[0].max_amount))
                
                
