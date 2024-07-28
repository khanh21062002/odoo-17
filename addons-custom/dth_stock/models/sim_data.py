from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class SimData(models.Model):
    _name = 'dth.kho.sim.data'
    _description = 'Số sim'
    _inherit = ['mail.thread']
    _display_name = 'name_full'
    _order = 'write_date desc'
    
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', default=lambda self: self.env.ref('base.VND'))
    category_ids = fields.Many2many('dth.kho.sim.category', string='Loại sim', ondelete='restrict') # c2
    category_id = fields.Many2one('dth.kho.sim.category', string='Danh mục chính', ondelete='restrict') # c
    name = fields.Char(string='Số sim', compute='_compute_name', store=True, index=True)
    name_full = fields.Char(string='Số sim đầy đủ', size=14, required=True, index=True, tracking=True) #f
    commited = fields.Char(string='Cam kết') # ck
    sold = fields.Boolean(string='Đã bán')
    last_4_num = fields.Char(string='Bốn số cuối', size=4)
    num0 = fields.Integer(string='Số đầu', compute='_compute_num', store=True) #f0
    num1 = fields.Integer(string='Số thứ 2', compute='_compute_num', store=True) #f1
    num2 = fields.Integer(string='Số thứ 3', compute='_compute_num', store=True) #f2
    num3 = fields.Integer(string='Số thứ 4', compute='_compute_num', store=True) #f3
    num4 = fields.Integer(string='Số thứ 5', compute='_compute_num', store=True) #f4
    num5 = fields.Integer(string='Số thứ 6', compute='_compute_num', store=True) #f5
    num6 = fields.Integer(string='Số thứ 7', compute='_compute_num', store=True) #f6
    num7 = fields.Integer(string='Số thứ 8', compute='_compute_num', store=True) #f7
    num8 = fields.Integer(string='Số thứ 9', compute='_compute_num', store=True) #f8
    num9 = fields.Integer(string='Số thứ 10', compute='_compute_num', store=True) #f9
    hide_web = fields.Boolean(string='Ẩn trên web', default=False) #h
    hide_web_12h = fields.Boolean(string='Ẩn trên web 12h', default=False) #hg
    web_price_s = fields.Monetary(string='Giá web', currency_field='currency_id', group_operator=False, tracking=True, compute="_compute_web_price_s", store=True) #p
    # sell_price = fields.Monetary(string='Giá bán', currency_field='currency_id')
    # buy_price = fields.Monetary(string='Giá thu', currency_field='currency_id')
    original_price = fields.Monetary(string='Giá gốc', currency_field='currency_id') #pg
    pt_point = fields.Float(string='Điểm phong thủy')
    telecom_supplier_id = fields.Many2one('dth.kho.telecom.supplier', string='Nhà mạng', required=True, index=True, tracking=True, ondelete='restrict') #t
    telecom_supplier_code = fields.Integer(string="Mã nhà mạng", related='telecom_supplier_id.code', store=True, index=True)
    sub_type = fields.Selection([('tra_truoc', 'Trả trước'), ('tra_sau', 'Trả sau')], string='Loại thuê bao', required=True, tracking=True) #tt
    priority = fields.Integer(string='Điểm ưu tiên') #Ut
    priority_p = fields.Integer(string='Điểm ưu tiên theo giá') #Utp
    priority_c = fields.Integer(string='Điểm ưu tiên theo danh mục') #Utc
    priority_t = fields.Integer(string='Điểm ưu tiên theo nhà mạng') #Utt
    note = fields.Text(string='Ghi chú')
    package_ids = fields.Many2many('dth.kho.mobile.package', string='Gói cước', ondelete='restrict', domain="[('telecom_supplier_id', '=', telecom_supplier_id)]")
    sim_state = fields.Selection([('da_kh', 'Đã kích hoạt'), ('chua_kh', 'Chưa kích hoạt')], string='Tình trạng sim', tracking=True)
    sim_warehouse_ids = fields.One2many('dth.kho.sim.warehouse', 'sim_data_id', string='Kho sim')
    comment_history_ids = fields.One2many('dth.kho.comment.history', 'sim_data_id', string='Danh sách comment')
    lastest_upload_history_id = fields.Many2one('dth.kho.sim.upload.history', string='Lần up bảng gần nhất')
    first_3num = fields.Char(string='3 Số đầu')
    
    _sql_constraints = [
        ('sim_data_unique_name', 'unique(name)', "Số sim đã tồn tại")
    ]
    
    @api.constrains('name')
    def _check_name(self):
        for r in self:
            if r.name:
                if not self.check_phone_number_format(r.name):
                    raise ValidationError("Số sim phải bắt đầu bằng số 0 và bao gồm 10 chữ số.")
    
    @api.depends('name_full')
    def _compute_name(self):
        for r in self:
            r.name = ''
            if r.name_full:
                r.name = r.name_full.replace('.', '')
    
    @api.depends('name')
    def _compute_num(self):
        for r in self:
            if r.name:
                r.num0 = int(r.name[0])
                r.num1 = int(r.name[1])
                r.num2 = int(r.name[2])
                r.num3 = int(r.name[3])
                r.num4 = int(r.name[4])
                r.num5 = int(r.name[5])
                r.num6 = int(r.name[6])
                r.num7 = int(r.name[7])
                r.num8 = int(r.name[8])
                r.num9 = int(r.name[9])

    @api.depends('name_full')
    def _compute_display_name(self):
        for r in self:
            r.display_name = r.name_full
    
    @api.model
    def create(self, vals):
        if vals.get('name_full', False):
            name = vals.get('name_full', False).replace('.', '')
            dupplidate = self.env['dth.kho.sim.data'].search([('name', '=', name)], limit=1)
            if dupplidate:
                return dupplidate
        return super(SimData, self).create(vals)
    
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
    
    @api.depends('sim_warehouse_ids.sell_price_s', 'sim_warehouse_ids.sim_status')
    def _compute_web_price_s(self):
        for r in self:
            sim_warehouses = r.sim_warehouse_ids.filtered(lambda w: w.sim_status != 'da_ban')
            if sim_warehouses:
                r.web_price_s = min(sim_warehouses.mapped('sell_price_s'))
            else:
                r.web_price_s = r.sim_warehouse_ids and min(r.sim_warehouse_ids.mapped('sell_price_s')) or 0
