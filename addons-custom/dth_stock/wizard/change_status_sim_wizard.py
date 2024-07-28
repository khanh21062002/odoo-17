# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ChangeStatusSimWizard(models.TransientModel):
    _name = 'change.status.sim.wizard'
    _description = 'Wizard Chuyển trạng thái sim'

    sim_warehouse_id = fields.Many2one('dth.kho.sim.warehouse', string='Kho áp dụng')
    sim_name = fields.Char(string='Số sim', compute='_compute_sim_name')
    state = fields.Selection([('so_con', 'Số còn'), 
                              ('da_ban_co_chuong', 'Đã bán - Có đổ chuông'), 
                              ('da_ban_khong_chuong', 'Đã bán - Không đổ chuông'),
                              ('da_ban_check_tho', 'Đã bán - Check thợ'),
                              ('da_ban_nang_gia', 'Đã bán để nâng giá bán'),
                              ('da_ban_khach_yeu_cau', 'Đã bán khách yêu cầu gỡ bảng'),
                              ('da_ban_dau_chi_tieu', 'Đã bán đấu chỉ tiêu'),
                              ('sai_gia', 'Sai giá'),
                              ('da_co_nv_check', 'Đã có NV check trước')], string='Trạng thái', required=True)
    apply_all = fields.Boolean(string='Áp dụng với tất cả các kho', default=True)
    note = fields.Text(string='Ghi chú')
    comment_ids = fields.Many2many('dth.kho.comment.history', string='Lịch sử comment', compute='_compute_comment_ids', compute_sudo=True)
    
    @api.depends('sim_warehouse_id')
    def _compute_comment_ids(self):
        for r in self:
            r.comment_ids = r.sim_warehouse_id.sim_data_id.comment_history_ids.filtered(lambda h: h.apply_all)
    
    @api.depends('sim_warehouse_id')
    def _compute_sim_name(self):
        for r in self:
            r.sim_name = r.sim_warehouse_id.name_full
    
    def action_apply(self):
        state = ''
        sim_state = ''
        if self.state == 'so_con':
            state = 'Số còn'
            sim_state = 'so_con'
        elif self.state == 'da_ban_co_chuong':
            state = 'Đã bán - Có đổ chuông'
            sim_state = 'da_ban'
        elif self.state == 'da_ban_khong_chuong':
            state = 'Đã bán - Không đổ chuông'
            sim_state = 'da_ban'
        elif self.state == 'da_ban_check_tho':
            state = 'Đã bán - Check thợ'
            sim_state = 'da_ban'
        elif self.state == 'da_ban_nang_gia':
            state = 'Đã bán để nâng giá bán'
            sim_state = 'da_ban'
        elif self.state == 'da_ban_khach_yeu_cau':
            state = 'Đã bán khách yêu cầu gỡ bảng'
            sim_state = 'da_ban'
        elif self.state == 'da_ban_dau_chi_tieu':
            state = 'Đã bán đấu chỉ tiêu'
            sim_state = 'da_ban'
        elif self.state == 'sai_gia':
            state = 'Sai giá'
            sim_state = ''
        elif self.state == 'da_co_nv_check':
            state = 'Đã có NV check trước'
            sim_state = ''
        vals = {
                'sim_data_id': self.sim_warehouse_id.sim_data_id.id,
                'sim_warehouse_id': self.sim_warehouse_id.id,
                'state': state,
                'note': self.note,
                'apply_all': self.apply_all
            }
        if sim_state:
            if not self.apply_all:
                self.sim_warehouse_id.write({'sim_status': sim_state})
            else:
                if sim_state == 'da_ban':
                    self.sim_warehouse_id.sim_data_id.sim_warehouse_ids.write({'sim_status': sim_state})
        self.env['dth.kho.comment.history'].create(vals)
    
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': 'Comment thành công.',
                'next': {
                    'type': 'ir.actions.act_window_close'
                },
            }
        }