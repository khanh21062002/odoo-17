from odoo import models, fields, api
import re

class CommentHistory(models.Model):
    _name = 'dth.kho.comment.history'
    _description = 'Lịch sử comment'
    _order = 'create_date desc'

    sim_warehouse_id = fields.Many2one('dth.kho.sim.warehouse', string='Số sim', index=True)
    sim_data_id = fields.Many2one('dth.kho.sim.data', string='Danh sách sim', index=True)
    state = fields.Char(string='Trạng thái')
    note = fields.Text(string='Nội dung comment')
    comment_note = fields.Text(string="Comment hiển thị", compute='_compute_comment_note')
    apply_all = fields.Boolean(string='Áp dụng tất cả các kho', default=True)
    
    def read(self, fields=None, load='_classic_read'):
        if self.env.context.get('pass_security_history', False):
            self = self.sudo()
        return super(CommentHistory, self).read(fields=fields, load=load)
    
    def _compute_comment_note(self):
        for r in self:
            if r.note:
                list_note = r.note.split(' ')
                for i, note in enumerate(list_note):
                    if self.check_phone_number_format(note):
                        list_note[i] = self.replace_phone_number(note)
                comment_note = 'Giá cũ: %s  %s' % (self.env.ref('base.VND').format(r.sim_data_id.web_price_s), ' '.join(list_note))
            else:
                comment_note = 'Giá cũ: %s' % self.env.ref('base.VND').format(r.sim_data_id.web_price_s)
            r.comment_note = comment_note
    
    def check_number_format(self, str):
        regex = r'^[0-9]+$'
        if re.match(regex, str):
            return True
        else:
            return False
    
    def check_phone_number_format(self, str):
        valid = True
        if not str:
            valid = False
        else:
            if not self.check_number_format(str) or str[0] != '0' or len(str) != 10:
                valid = False
        return valid
    
    def replace_phone_number(self, str):
        return str.replace(str[3:7], '****')
    
    
