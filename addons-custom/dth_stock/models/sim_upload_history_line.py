import re
from odoo import models, fields, api

class SimUploadHistoryLine(models.Model):
    _name = 'dth.kho.sim.upload.history.line'
    _description = 'Chi tiết lịch sử Up sim'
    _order = 'abnormal desc, create_date desc, sim_name_clear'

    sim_name = fields.Char(string='Số sim')
    sim_name_clear = fields.Char(string='Số sim không format')
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', default=lambda self: self.env.ref('base.VND'))
    upload_history_id = fields.Many2one('dth.kho.sim.upload.history', string='Lịch sử up sim')
    sim_maker_id = fields.Many2one('dth.kho.sim.maker', related='upload_history_id.sim_maker_id', string='Thợ sim', index=True)
    sell_price_s = fields.Char(string='Giá bán')
    buy_price_s = fields.Char(string='Giá thu')
    profit = fields.Monetary(string='Lợi nhuận thợ')
    telecom_supplier_id = fields.Many2one('dth.kho.telecom.supplier', string='Nhà mạng')
    category_ids = fields.Many2many('dth.kho.sim.category', string='Loại sim')
    sub_type = fields.Selection([('1', 'Trả trước'), ('0', 'Trả sau')], string='Loại thuê bao')
    sim_state = fields.Selection([('da_kh', 'Đã kích hoạt'), ('chua_kh', 'Chưa kích hoạt')], string='Tình trạng')
    # package_ids = fields.Many2many('dth.kho.mobile.package', string='Gói cước')
    commited = fields.Char(string='Cam kết')
    note = fields.Text(string='Ghi chú')
    abnormal = fields.Boolean(string='Bất thường')
    old_new = fields.Selection([('old', 'Số sim cũ'), ('new', 'Số sim mới')], string='Cũ mới')
    state = fields.Selection(related='upload_history_id.state', store=True)
    
    def check_abnormal(self):
        if not self.sim_name or not self.sell_price_s or not self.buy_price_s or not self.telecom_supplier_id:
            return False
        if not self.check_phone_number_format(self.sim_name.replace('.', '').strip()):
            return False
        if not self.check_number_format(self.sell_price_s) or not self.check_number_format(self.buy_price_s):
            return False
        if int(self.sell_price_s) < 100000 or int(self.buy_price_s) < 100000:
            return False
        sql = """
            SELECT id FROM dth_kho_sim_upload_history_line WHERE upload_history_id = %s AND sim_name_clear = '%s'
        """ % (self.upload_history_id.id, self.sim_name_clear)
        self.env.cr.execute(sql)
        lines = self.env.cr.dictfetchall() 
        if len(lines) > 1:
            return False
        return True
    
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

class SimUploadHistoryLineStore(models.Model):
    _name = 'dth.kho.sim.upload.history.line.store'
    _inherit = 'dth.kho.sim.upload.history.line'
    _description = 'Chi tiết lịch sử Up sim lưu trữ'
    _order = 'abnormal desc, create_date desc'
