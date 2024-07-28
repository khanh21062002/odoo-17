# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SimMakerRatingWizard(models.TransientModel):
    _name = 'sim.maker.rating.wizard'
    _description = 'Wizard đánh giá thợ sim'

    sim_maker_id = fields.Many2one('dth.kho.sim.maker', string='Thợ sim')
    rating = fields.Selection([('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], required=True, string='Điểm đánh giá')
    description = fields.Text(string='Nội dung', required=True)
    
    @api.constrains('description')
    def _check_description(self):
        for r in self:
            if len(r.description) < 2 or len(r.description) > 255:
                raise ValidationError('Nội dung đánh giá phải có độ dài từ 2-255 ký tự.')

    def action_apply(self):
        if self.sim_maker_id and self.rating:
            self.env['dth.kho.sim.maker.rating'].create({
                    'sim_maker_id': self.sim_maker_id.id,
                    'rating': self.rating,
                    'description': self.description
                })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'message': 'Đánh giá chất lượng thợ thành công',
                    'next': {
                        'type': 'ir.actions.act_window_close'
                    },
                }
            }