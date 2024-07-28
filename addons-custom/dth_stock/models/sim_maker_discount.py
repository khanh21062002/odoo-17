from odoo import models, fields, api
from odoo.tools import float_is_zero
from odoo.exceptions import UserError, ValidationError

class SimMakerDiscount(models.Model):
    _name = 'dth.kho.sim.maker.discount'
    _description = 'Chiết khấu'
    _order = 'min_amount'

    sim_maker_id = fields.Many2one('dth.kho.sim.maker', string='Thợ sim', ondelete='cascade', index=True)
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', default=lambda self: self.env.ref('base.VND'))
    min_amount = fields.Monetary(string='Giá min', currency_field='currency_id', required=True)
    max_amount = fields.Monetary(string='Giá max', currency_field='currency_id', required=True)
    discount = fields.Float(string='Chiết khấu', required=True)
    
    @api.constrains('discount')
    def _check_discount(self):
        for r in self:
            if r.discount <= 0 or r.discount > 1:
                raise ValidationError('Chiếu khấu: Giá trị phần trăm chiết khấu phải nằm trong khoảng 1-100.')
    
    @api.constrains('min_amount', 'max_amount')
    def _constrains_amount(self):
        for r in self:
            if r.min_amount < 0 or r.max_amount < 0:
                raise ValidationError('Chiết khấu: Giá min và giá max phải lớn hơn hoặc bằng 0.')
            if not float_is_zero(r.max_amount, precision_rounding=2) and r.min_amount >= r.max_amount:
                raise ValidationError('Chiết khấu: Giá max phải lớn hơn giá min, nếu muốn để giá max là vô hạn, bạn đặt giá max về 0.')
            domain = []
            if not float_is_zero(r.max_amount, precision_rounding=2):
                domain = [('sim_maker_id', '=', r.sim_maker_id.id),
                         ('id', '!=', r.id),
                         '|', '&', '&',('max_amount', '>', 0),
                                ('min_amount', '<=', r.max_amount),
                                ('max_amount', '>=', r.min_amount),
                                '&', ('max_amount', '=', 0),
                                ('min_amount', '<=', r.max_amount)]
            else:
                domain = [('sim_maker_id', '=', r.sim_maker_id.id),
                         ('id', '!=', r.id),
                         '|', '&',('max_amount', '>', 0),
                                ('max_amount', '>=', r.min_amount),
                                ('max_amount', '=', 0)]
            overlap_supports = self.env['dth.kho.sim.maker.discount'].search(domain, limit=1)
            if overlap_supports:
                raise ValidationError('Chiết khấu: Khoảng giá vừa tạo (điều chỉnh) bị chồng lấn với khoảng giá từ %s đến %s đã tạo trước đó.' % (overlap_supports[0].min_amount, overlap_supports[0].max_amount))
