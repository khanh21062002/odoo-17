# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    @api.model
    def _default_upload_sim_noti_user_ids(self):
        return self.env.ref("dth_stock.group_stock_manager").users.filtered(lambda u: not u.has_group('base.group_system'))
    
    upload_sim_noti_user_ids = fields.Many2many('res.users', string='Người dùng nhận thông báo up bảng', default=_default_upload_sim_noti_user_ids)
    sim_maker_ids = fields.Many2many('dth.kho.sim.maker', string='Nhập mã kho')
    according_network = fields.Many2many('dth.kho.telecom.supplier', string='Theo nhà mạng')
    by_sim_type = fields.Many2many('dth.kho.sim.category', string='Theo loại sim')