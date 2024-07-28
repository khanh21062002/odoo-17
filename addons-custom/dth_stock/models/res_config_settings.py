# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import re
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rating_interval_days = fields.Integer(string="Thời hạn tái đánh giá thợ sim", default=0,
                                          config_parameter='rating_interval_days',
                                          help="Khoảng thời gian (tính theo ngày) giữa 2 kỳ đánh giá thợ sim của một user.") 
    upload_sim_noti_user_ids = fields.Many2many('res.users', string='Người dùng nhận thông báo up bảng', related='company_id.upload_sim_noti_user_ids',
                                                readonly=False, help="Người dùng sẽ nhận được thông báo trong các trường hợp: bảng số được up tự động và bảng số được xử lý xong và up vào kho thành công.")
    upload_received_email = fields.Char(string='Email nhận up bảng', config_parameter='upload_received_email')
    
    # Data pipeline: Thông tin sẽ được lưu vào bảng ir_config_parameter
    new_sim_number = fields.Float(string='Số sim mới từ', default=0, config_parameter='new_sim_number')
    sold_sim_number = fields.Float(string='Số sim đã bán từ', default=0, config_parameter='sold_sim_number')
    selling_price_increased = fields.Float(string='Giá bán tăng từ', default=0, config_parameter='selling_price_increased')
    selling_price_decreased = fields.Float(string='Giá bán giảm từ', default=0, config_parameter='selling_price_decreased')
    revenue_increases = fields.Float(string='Giá thu tăng từ', default=0, config_parameter='revenue_increases')
    revenue_decreased = fields.Float(string='Giá thu giảm từ', default=0, config_parameter='revenue_decreased')

    # Danh sách nháy máy
    warehouse_type = fields.Selection([
        ('kho_nha', 'Kho nhà'),
        ('kho_uu_tien', 'Kho ưu tiên'),
        ('tang_hien_thi', 'Tăng hiển thị'),
    ], string="Loại kho", config_parameter="flash_list_warehouse_type")
    sim_maker_ids = fields.Many2many('dth.kho.sim.maker', string='Nhập mã kho', related='company_id.sim_maker_ids', readonly=False, help='Nhập mã kho') # Được lưu tại dth_sim_maker_res_company_rel
    sim_maker_ids_domain = fields.Binary(compute="_compute_sim_maker_ids_domain", string='Nhập mã kho domain')
    uptime = fields.Float(string="Theo thời gian up", config_parameter='flash_list_uptime', default=0)
    combobox_min_price = fields.Selection([
        ('0', '0 Đồng'),
        ('500000', '500 Nghìn'), 
        ('1000000', '1 Triệu'),
        ('3000000', '3 Triệu'),
        ('5000000', '5 Triệu'),
        ('10000000', '10 Triệu'),
        ('30000000', '30 Triệu'),
        ('50000000', '50 Triệu'),
        ('100000000', '100 Triệu'),
        ('200000000', '200 Triệu'),
        ('500000000', '500 Triệu'),
        ('1000000000', '1 Tỷ'),
    ], string="Theo giá sim min")
    min_price = fields.Float(string="Theo giá sim min", config_parameter='flash_list_min_price', default=0)
    combobox_max_price = fields.Selection([
        ('500000', '500 Nghìn'), 
        ('1000000', '1 Triệu'),
        ('3000000', '3 Triệu'),
        ('5000000', '5 Triệu'),
        ('10000000', '10 Triệu'),
        ('30000000', '30 Triệu'),
        ('50000000', '50 Triệu'),
        ('100000000', '100 Triệu'),
        ('200000000', '200 Triệu'),
        ('500000000', '500 Triệu'),
        ('1000000000', '1 Tỷ'),
    ], string="Theo giá sim max")
    max_price = fields.Float(string="Theo giá sim max", config_parameter='flash_list_max_price', default=0)
    according_network = fields.Many2many('dth.kho.telecom.supplier', string='Theo nhà mạng', related='company_id.according_network', readonly=False)
    by_sim_type = fields.Many2many('dth.kho.sim.category', string='Theo loại sim', related='company_id.by_sim_type', readonly=False)

    # API và Kafka
    url_kafka_bootstrap_servers = fields.Char(string='Kafka bootstrap servers',config_parameter='url_kafka_bootstrap_servers')
    url_api_up_file = fields.Char(string='URL API Up File',config_parameter='url_api_up_file')
    url_api_calculates_collection_price = fields.Char(string='URL API tính giá thu',config_parameter='url_api_calculates_collection_price')

    def check_email_format(self, str):
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(regex, str):
            return False
        vals = str.split('@')
        if len(vals[0]) < 5 or len(vals[0]) > 32:
            return False
        return True

    @api.constrains('upload_received_email')
    def _check_email(self):
        for r in self:
            if r.upload_received_email:
                if not self.check_email_format(r.upload_received_email):
                    raise ValidationError("Email chưa đúng định dạng. Phần Username phải từ 5-32 ký tự.")

    @api.depends('warehouse_type')
    def _compute_sim_maker_ids_domain(self):
        for rec in self:
            domain = []
            if rec.warehouse_type == 'kho_nha':
                domain = [('dth_wh', '=', True)]
            elif rec.warehouse_type == 'kho_uu_tien':
                domain = [('priority_wh', '=', True)]
            elif rec.warehouse_type == 'tang_hien_thi':
                domain = [('increase_show', '=', True)]
            rec.sim_maker_ids_domain = domain

    @api.onchange('combobox_min_price')
    def _onchange_combobox_min_price(self):
        if self.combobox_min_price:
            self.min_price = float(self.combobox_min_price)
    
    @api.onchange('combobox_max_price')
    def _onchange_combobox_max_price(self):
        if self.combobox_max_price:
            self.max_price = float(self.combobox_max_price)

    @api.constrains('min_price', 'max_price')
    def _check_price(self):
        for r in self:
            if r.min_price > r.max_price:
                raise ValidationError("Giá min phải nhỏ hơn giá max.")