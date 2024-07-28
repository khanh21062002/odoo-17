from odoo import models, fields, api

class SimMakerRating(models.Model):
    _name = 'dth.kho.sim.maker.rating'
    _description = 'Đánh giá thợ'

    sim_maker_id = fields.Many2one('dth.kho.sim.maker', string='Thợ sim', ondelete='cascade', index=True)
    rating = fields.Selection([('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], default="1", required=True, string='Điểm đánh giá')
    description = fields.Text(string='Nội dung')
    