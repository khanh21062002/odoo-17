import xlsxwriter
from io import BytesIO
import base64
import os
import json
from datetime import datetime

from odoo import models, fields, api
from odoo.tools import float_round
from odoo.exceptions import UserError, ValidationError
import re
from odoo.http import request, content_disposition
from odoo.osv import expression
from curses.ascii import EM

class SimMaker(models.Model):
    _name = 'dth.kho.sim.maker'
    _inherit = ['mail.thread']
    _description = "Thợ sim"
    _order = 'create_date desc, id desc'
    
    name = fields.Char(string='Tên thợ', required=True, tracking=True, size=255)
    code = fields.Char(string='Mã thợ', required=True, index=True, tracking=True, size=4)
    phone_number = fields.Text(string='Số điện thoại', tracking=True, required=True, index=True, help="Nhập tối đa 3 số điện thoại trên 3 dòng.")
    hotline_check = fields.Text(string='Hotline check số', tracking=True, help="Nhập tối đa 5 số hotline trên 5 dòng.")
    hotline_make_sim = fields.Text(string='Hotline làm sim', tracking=True, help="Nhập tối đa 5 số hotline trên 5 dòng.")
    hotline_debt = fields.Text(string='Hotline công nợ', tracking=True, help="Nhập tối đa 5 số hotline trên 5 dòng.")
    hotline_feedback = fields.Text(string='Hotline góp ý, khiếu nại', tracking=True, help="Nhập tối đa 5 số hotline trên 5 dòng.")
    email = fields.Text(string='Email', required=True, tracking=True, index=True, help="Nhập tối đa 3 địa chỉ email trên 3 dòng.")
    province_id = fields.Many2one('res.country.province', string='Tỉnh thành', index=True, tracking=True)
    district_id = fields.Many2one('res.country.district', string='Quận/huyện', domain="[('province_id', '=', province_id)]", index=True, tracking=True)
    ward_id = fields.Many2one('res.country.ward', string='Phường/xã', domain="[('district_id', '=', district_id)]", index=True, tracking=True)
    address = fields.Char(string='Địa chỉ chi tiết')
    zalo = fields.Char(string='Zalo', index=True, tracking=True)
    facebook = fields.Char(string='Facebook', index=True, tracking=True, size=255)
    website = fields.Char(string='Website', tracking=True, size=255)
    dth_wh = fields.Boolean(string='Kho nhà', default=False, help='Kho của DTH', tracking=True)
    monopoly_wh = fields.Boolean(string='Kho độc quyền', default=False, help='Kho bao gồm các số sim mà chỉ DTH mới có', tracking=True)
    priority_wh = fields.Boolean(string='Kho ưu tiên', default=False, help='Kho được ưu tiên cho các mục đích kinh doanh', tracking=True)
    mapping_wh = fields.Boolean(string='Kho ánh xạ', default=False, help='Kho tổng hợp các số sim ưu tiên từ các kho khác cho mục đích kinh doanh, không phải kho thợ thật', tracking=True)
    auto_sms = fields.Boolean(string='Auto SMS', default=False, help='Tự động gửi SMS giữ số tới thợ khi có khách đặt mua số sim của thợ', tracking=True)
    note = fields.Text(string='Ghi chú')
    bank_account_ids = fields.One2many('dth.kho.bank.account', 'sim_maker_id', string='Tài khoản ngân hàng')
    discount_ids = fields.One2many('dth.kho.sim.maker.discount', 'sim_maker_id', string='Chiết khấu', required=True)
    support_ids = fields.One2many('dth.kho.sim.maker.support', 'sim_maker_id', string='Hỗ trợ')
    installment_ids = fields.One2many('dth.kho.sim.maker.installment', 'sim_maker_id', string='Trả góp', required=True)
    work_time = fields.Char(string='Thời gian làm việc', tracking=True)
    self_cod = fields.Boolean(string='Thợ tự COD', default=False, tracking=True)
    installment = fields.Boolean(string='Cho phép trả góp', default=False, tracking=True)
    debt = fields.Boolean(string='Làm công nợ', default=False, tracking=True)
    #total_rating = fields.Float(string='Đánh giá', compute='_compute_total_rating', store=True, digits=(1, 1), compute_sudo=True)
    sim_count = fields.Integer(string='Tổng số sim', readonly=True, compute='_compute_sim_count', store=True)
    sim_sold_count = fields.Integer(string='Số sim đã bán', readonly=True, compute='_compute_sim_sold_count', store=True)
    contact = fields.Text(string='Liên hệ', compute='_compute_contact', store=True)
    sale_person_id = fields.Many2one('res.users', string='Nhân viên kinh doanh', index=True, tracking=True)
    reponsible_ids = fields.Many2many('res.users', string='Users phụ trách')
    active = fields.Boolean(default=True)
    increase_show = fields.Boolean(string='Tăng hiển thị', default=False, tracking=True, help="Tăng hoặc giảm tần suất hiển thị số sim của kho trên web bán hàng")
    keep_price = fields.Boolean(string='Giữ nguyên giá', default=False, tracking=True, help="Giữ nguyên giá hoặc bỏ giữ nguyên giá của thợ sim khi up bảng")
    sim_visible = fields.Selection([('show', 'Hiển thị'), ('part_hide', 'Ẩn một phần'), ('hide', 'Ẩn toàn bộ')], default='show', string='Hiển thị số sim', tracking=True)
    #rating_ids = fields.One2many('dth.kho.sim.maker.rating', 'sim_maker_id', string='Lượt đánh giá')
    hotline = fields.Text(string='Hotline', tracking=True)
    sim_warehouse_ids = fields.One2many('dth.kho.sim.warehouse', 'sim_maker_id', string='Kho sim')
    upload_history_ids = fields.One2many('dth.kho.sim.upload.history', 'sim_maker_id', string='Danh sách up bảng')
    upload_history_done_ids = fields.One2many('dth.kho.sim.upload.history', string='Danh sách up bảng hoàn thành', compute='_compute_upload_history_done_ids')
    peel_wh = fields.Boolean(string='Kho bóc số', default=False, tracking=True)
    
    _sql_constraints = [
        ('sim_maker_unique_code', 'unique(code)', "Mã thợ đã tồn tại")
    ]
    
    # @api.constrains('code')
    # def _check_code(self):
    #     for r in self:
    #         if r.code and (len(r.code) != 4 or not self.check_number_format(r.code) or r.code[0] == '0'):
    #             raise ValidationError("Mã thợ phải gồm 4 chữ số, không bắt đầu từ số 0.") 
    #
    # @api.constrains('phone_number')
    # def _check_phone_number(self):
    #     for r in self:
    #         if r.phone_number:
    #             phone_numbers = r.phone_number.split('\n')
    #             phone_numbers = [phone.strip() for phone in phone_numbers if phone.strip()]
    #             if '' in phone_numbers:
    #                 phone_numbers.remove('')
    #             if len(phone_numbers) > 3 or any(not self.check_phone_number_format(phone_number.strip()) for phone_number in phone_numbers):
    #                 raise ValidationError("Số điện thoại phải bắt đầu bằng số 0 và bao gồm 10 chữ số. Chỉ được nhập tối đa 3 số điện thoại trên 3 dòng.")
    #             no_dupplicate_phone_numbers = set(phone_numbers)
    #             if len(phone_numbers) != len(no_dupplicate_phone_numbers):
    #                 raise ValidationError("Số điện thoại trên các dòng không được trùng nhau.")
    #             # Xác định câu lệnh SQL và placeholders
    #             query = """
    #                 SELECT COUNT(id) 
    #                 FROM dth_kho_sim_maker 
    #                 WHERE id != %s AND ({})
    #             """.format(" OR ".join(["phone_number LIKE %s"] * len(phone_numbers)))
    #             # Tạo danh sách tham số
    #             arr = [r.id]
    #             for phone_number in phone_numbers:
    #                 arr.append(f'%{phone_number}%')
    #             params = tuple(arr)
    #             # Thực thi truy vấn SQL
    #             self.env.cr.execute(query, params)
    #             existing_phone_numbers = self.env.cr.fetchone()[0]
    #             if existing_phone_numbers >= 1:
    #                 raise ValidationError("Ít nhất một số điện thoại trùng với số điện thoại đã tồn tại của thợ sim khác.")
    #
    #
    # @api.constrains('hotline_check')
    # def _check_hotline_check(self):
    #     for r in self:
    #         if r.hotline_check:
    #             hotlines = r.hotline_check.split('\n')
    #             if '' in hotlines:
    #                 hotlines.remove('')
    #             if len(hotlines) > 5 or any(not self.check_hotline_format(hotline.strip()) for hotline in hotlines):
    #                 raise ValidationError("Hotline check số phải bao gồm từ 8 - 11 chữ số. Chỉ được nhập tối đa 3 số hotline trên 3 dòng.")
    #
    # @api.constrains('hotline_make_sim')
    # def _check_hotline_make_sim(self):
    #     for r in self:
    #         if r.hotline_make_sim:
    #             hotlines = r.hotline_make_sim.split('\n')
    #             if '' in hotlines:
    #                 hotlines.remove('')
    #             if len(hotlines) > 5 or any(not self.check_hotline_format(hotline.strip()) for hotline in hotlines):
    #                 raise ValidationError("Hotline làm sim phải bao gồm từ 8 - 11 chữ số. Chỉ được nhập tối đa 5 số hotline trên 5 dòng.")
    #
    # @api.constrains('hotline_debt')
    # def _check_hotline_debt(self):
    #     for r in self:
    #         if r.hotline_debt:
    #             hotlines = r.hotline_debt.split('\n')
    #             if '' in hotlines:
    #                 hotlines.remove('')
    #             if len(hotlines) > 5 or any(not self.check_hotline_format(hotline.strip()) for hotline in hotlines):
    #                 raise ValidationError("Hotline công nợ phải bao gồm từ 8 - 11 chữ số. Chỉ được nhập tối đa 5 số hotline trên 5 dòng.")
    #
    # @api.constrains('hotline_feedback')
    # def _check_hotline_feedback(self):
    #     for r in self:
    #         if r.hotline_feedback:
    #             hotlines = r.hotline_feedback.split('\n')
    #             if '' in hotlines:
    #                 hotlines.remove('')
    #             if len(hotlines) > 5 or any(not self.check_hotline_format(hotline.strip()) for hotline in hotlines):
    #                 raise ValidationError("Hotline góp ý, khiếu nại phải bao gồm từ 8 - 11 chữ số. Chỉ được nhập tối đa 5 số hotline trên 5 dòng.")
    #
    # @api.constrains('zalo')
    # def _check_zalo(self):
    #     for r in self:
    #         if r.zalo:
    #             if not self.check_phone_number_format(r.zalo):
    #                 raise ValidationError("Số điện thoại đăng ký Zalo phải bắt đầu bằng số 0 và bao gồm 10 chữ số.")
    #
    # @api.constrains('email')
    # def _check_email(self):
    #     for r in self:
    #         if r.email:
    #             emails = r.email.split('\n')
    #             emails = [email.strip() for email in emails if email.strip()]
    #             if '' in emails:
    #                 emails.remove('')
    #             if len(emails) > 3 or any(not self.check_email_format(email.strip()) for email in emails):
    #                 raise ValidationError("Email chưa đúng định dạng. Phần Username phải từ 5-32 ký tự. Chỉ được nhập tối đa 3 email trên 3 dòng.")
    #             no_dupplicate_emails = set(emails)
    #             if len(emails) != len(no_dupplicate_emails):
    #                 raise ValidationError("Địa chỉ email trên các dòng không được trùng nhau.")
    #             # Xác định câu lệnh SQL và placeholders
    #             query = """
    #                 SELECT COUNT(id) 
    #                 FROM dth_sim_maker 
    #                 WHERE id != %s AND ({})
    #             """.format(" OR ".join(["email LIKE %s"] * len(emails)))
    #             # Tạo danh sách tham số
    #             arr = [r.id]
    #             for email in emails:
    #                 arr.append(f'%{email}%')
    #             params = tuple(arr)
    #             # Thực thi truy vấn SQL
    #             self.env.cr.execute(query, params)
    #             existing_email = self.env.cr.fetchone()[0]
    #             if existing_email >= 1:
    #                 raise ValidationError("Ít nhất một email trùng với email đã tồn tại của thợ sim khác")

    
    @api.constrains('work_time')
    def _check_work_time(self):
        for r in self:
            if r.work_time:
                if not self.check_work_time_format(r.work_time):
                    raise ValidationError("Thời gian làm việc phải có định dạng hh:mm - hh:mm.")
    
    @api.depends('sim_warehouse_ids')
    def _compute_sim_count(self):
        for r in self:
            r.sim_count = len(r.sim_warehouse_ids)
    
    @api.depends('sim_warehouse_ids.sim_status')
    def _compute_sim_sold_count(self):
        for r in self:
            r.sim_sold_count = len(r.sim_warehouse_ids.filtered(lambda s: s.sim_status == 'da_ban'))
    
    @api.depends('code', 'name')
    def _compute_display_name(self):
        for r in self:
            if r.code and r.name:
                r.display_name = f"({r.code}) {r.name}"
            else:
                r.display_name = ''
                
    @api.onchange('province_id')
    def _onchange_province_id(self):
        self.district_id = False
        self.ward_id = False
    
    @api.onchange('district_id')
    def _onchange_district_id(self):
        self.ward_id = False
    
    def _compute_upload_history_done_ids(self):
        for r in self:
            r.upload_history_done_ids = r.upload_history_ids.filtered(lambda h: h.state == 'done')
    
    @api.depends('phone_number', 'email')
    def _compute_contact(self):
        for r in self:
            r.contact = ''
            if r.phone_number and r.email:
                phone_numbers = r.phone_number.split('\n')
                emails = r.email.split('\n')
                r.contact = phone_numbers[0] + '\n' + emails[0]
                
    # @api.depends('rating_ids')
    # def _compute_total_rating(self):
    #     for r in self:
    #         r.total_rating = 0
    #         if r.rating_ids:
    #             r.total_rating = float_round(sum([int(rating.rating) for rating in r.rating_ids]) / len(r.rating_ids), precision_digits=1)
    
    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            if operator in ('=', '!='):
                name_domain = ['|', ('code', '=', name.split(' ')[0]), ('name', operator, name)]
            else:
                name_domain = ['|', ('code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                name_domain = ['&', '!'] + name_domain[1:]
            domain = expression.AND([name_domain, domain])
        return self._search(domain, limit=limit, order=order)
    
    def open_rating(self):
        rating_interval_days = int(self.env['ir.config_parameter'].sudo().get_param('rating_interval_days', 0))
        if rating_interval_days > 0:
            last_rating = self.env['dth.kho.sim.maker.rating'].search([('create_uid', '=', self.env.user.id), 
                                                               ('sim_maker_id', '=', self.id)], 
                                                               order='create_date DESC', limit=1)
            if last_rating:
                number_of_days = (datetime.now() - last_rating.create_date).days + 1
                message = "Bạn đã đánh giá thợ sim này vào ngày %s. Bạn cần chờ thêm %s ngày nữa để có thể tiếp tục đánh giá thợ sim này." % (last_rating.create_date.strftime("%d/%m/%Y"), str(rating_interval_days - number_of_days))
                if rating_interval_days > number_of_days:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'type': 'danger',
                            'message': message,
                            'next': {
                                'type': 'ir.actions.act_window_close'
                            },
                        }
                    }
        
        action = self.env.ref('dth_stock.sim_maker_rating_wizard_action').sudo().read()[0]
        return action
    
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
    
    def check_hotline_format(self, str):
        valid = True
        if not str:
            valid = False
        else:
            if not self.check_number_format(str) or len(str) > 11 or len(str) < 8:
                valid = False
        return valid
    
    def check_email_format(self, str):
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(regex, str):
            return False
        vals = str.split('@')
        if len(vals[0]) < 5 or len(vals[0]) > 32:
            return False
        return True
    
    def check_work_time_format(self, str):
        regex = r'^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9] - (0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$'
        if re.match(regex, str):
            return True
        return False
        
    def download_sim_maker(self):
        datas = self.get_data()
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        worksheet = workbook.add_worksheet()
        worksheet.set_landscape()
        worksheet.fit_to_pages(1, 0)
        
        worksheet.set_column(0, 0, 5)#STT
        worksheet.set_column(1, 1, 10)#Mã thợ
        worksheet.set_column(2, 2, 20)#Tên thợ
        worksheet.set_column(3, 3, 35)#SĐT
        worksheet.set_column(4, 4, 35)#Email
        worksheet.set_column(5, 5, 25)#Website
        worksheet.set_column(6, 6, 15)#Số lượng sim
        worksheet.set_column(7, 7, 25)#Ngày cập nhật
        worksheet.set_column(8, 8, 15)#Tỉnh thành
        worksheet.set_column(9, 9, 15)#Phân loại
        worksheet.set_column(10, 10, 30)#STK1
        worksheet.set_column(11, 11, 30)#STK2
        worksheet.set_column(12, 12, 30)#STK3
        worksheet.set_column(13, 13, 30)#STK4
        
        name_style_format = workbook.add_format({'bold': True,
                                           'bottom': 1,
                                           'align':'center',
                                           'valign': 'vcenter',
                                           'text_wrap': True,
                                           'border': 1,
                                           'font_name': 'Times New Roman',
                                           'font_size': 13})
        
        worksheet.write(0, 0, 'STT', name_style_format)
        worksheet.write(0, 1, 'Mã kho', name_style_format)
        worksheet.write(0, 2, 'Tên thợ', name_style_format)
        worksheet.write(0, 3, 'Số điện thoại', name_style_format)
        worksheet.write(0, 4, 'Email', name_style_format)
        worksheet.write(0, 5, 'Website', name_style_format)
        worksheet.write(0, 6, 'Số lượng sim', name_style_format)
        worksheet.write(0, 7, 'Ngày cập nhật', name_style_format)
        worksheet.write(0, 8, 'TỈnh thành', name_style_format)
        worksheet.write(0, 9, 'Phân loại', name_style_format)
        col = 9
        for bn in range(1, self.get_max_number_bank() + 1):
            worksheet.write(0, col + bn, 'STK %s' % str(bn), name_style_format)
        
        row = 1
        for data in datas:
            for i in range(0, len(data)):
                worksheet.write(row, i, data[i])
            row += 1
        workbook.close()
        # Back cusor the beginning of the file
        file_data.seek(0)
        out = base64.encodebytes(file_data.getvalue())
        file_data.close()
        wizard = self.env['sim.maker.download.wizard'].create({'data': out})
        
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/sim.maker.download.wizard/%s/%s/%s' % (
                wizard.id, 'data', 'danhsachtho'),
            'target': 'new',
        } 
    
    def get_data(self):
        data = []
        stt = 1
        sim_makers = self.env['dth.kho.sim.maker'].browse(self.env.context.get('active_ids', [])).exists()
        for rec in sim_makers:
            val = [
                stt,
                rec.code or '',
                rec.name or '',
                ' - '.join(rec.phone_number.split('\n')) or '',
                ' - '.join(rec.email.split('\n')) or '',
                rec.website or '',
                rec.sim_count or 0,
                rec.write_date.strftime("%d/%m/%Y %H:%M:%S"),
                rec.province_id.name or '',
                rec.increase_show and 'VIP' or '',
            ]
            for bank_account in rec.bank_account_ids:
                val.append('%s - %s - %s' % (bank_account.bank, bank_account.account_number, bank_account.account_name))
            data.append(val)
            stt += 1
        return data
    
    def get_max_number_bank(self):
        sim_makers = self.env['dth.kho.sim.maker'].browse(self.env.context.get('active_ids', [])).exists()
        max_bank = 0
        if sim_makers:
            max_bank = max([len(sim_maker.bank_account_ids) for sim_maker in sim_makers])
        return max_bank
    
    def unlink(self):
        for r in self:
            if r.sim_warehouse_ids:
                raise ValidationError('Không thể xóa kho đã tồn tại số sim.')
        return super(SimMaker, self).unlink()
    
    def upload_file(self):
        action = self.env.ref('dth_stock.action_sim_upload_history').sudo().read()[0]
        action['context'] = {'default_sim_maker_id': self.id}
        return action
    
    def migrate_data(self):
        module_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(module_path, '..', 'data', 'thosim.json')
        file_path = os.path.normpath(file_path)
        file = open(file_path, 'r')
        kho = []
        for line in file:
            data = json.loads(line)
            kho_data = {'code' : data.get('_id'), 'name': data.get('name')}
            if data.get('contact', False):
                contact = self.process_old_data_phone_number(data.get('contact', False))
                kho_data['phone_number'] = contact
            if data.get('hotline', False):
                hotline = self.process_old_data_phone_number(data.get('hotline', False))
                if not kho_data.get('phone_number', False):
                    kho_data['phone_number'] = hotline
                kho_data['hotline_check'] = hotline
            if not kho_data.get('phone_number', False):
                kho_data['phone_number'] = '0000000000'
            if data.get('email', False):
                kho_data['email'] = self.process_old_data_email(data.get('email', False))
            else:
                kho_data['email'] = 'example@gmail.com'
            if data.get('web', False):
                kho_data['website'] = data.get('web', False)
            if data.get('facebook', False):
                kho_data['facebook'] = data.get('facebook', False)
            if data.get('diachi', False):
                kho_data['address'] = data.get('diachi', False)
            if data.get('ghichu', False):
                kho_data['note'] = data.get('ghichu', False)
            if data.get('tinhthanh', False):
                province = self.env['res.country.province'].search([('name', 'ilike', data.get('tinhthanh', False))], limit=1)
                if province:
                    kho_data['province_id'] = province.id
            if data.get('quanhuyen', False):
                district = self.env['res.country.district'].search([('name', 'ilike', data.get('quanhuyen', False))], limit=1)
                if province:
                    kho_data['district_id'] = district.id
            if data.get('hide', False) == 1:
                kho_data['sim_visible'] = 'hide'
            else:
                kho_data['sim_visible'] = 'show'
            if data.get('level', False) == 1:
                kho_data['increase_show'] = True
            else:
                kho_data['increase_show'] = False
            if data.get('giugia', False) == 1:
                kho_data['keep_price'] = True
            else:
                kho_data['keep_price'] = False
            if data.get('auto_sms', False) == 1:
                kho_data['auto_sms'] = True
            else:
                kho_data['auto_sms'] = False
            if data.get('chietkhau', False):
                discount = data.get('chietkhau', False).replace('\n', '')
                if discount.isdigit():
                    if int(discount) > 0:
                        kho_data['discount_ids'] = [(0, 0, {
                                'min_amount': 0,
                                'max_amount': 0,
                                'discount': int(discount)/100
                            })]
                else:
                    discount_vals = []
                    discounts = discount.split(';')
                    max_amount = 0
                    for dis in discounts:
                        pattern = re.compile(r'\d+\.\d+|\d+')
                        numbers = pattern.findall(dis)
                        if len(numbers) == 2:
                            if int(numbers[0]) > max_amount and max_amount != 0:
                                continue
                            discount_vals.append((0, 0, {
                                'min_amount': int(numbers[0]),
                                'max_amount': max_amount,
                                'discount': 1 - float(numbers[1])
                            }))
                            max_amount = int(numbers[0]) - 1
                        elif len(numbers) == 1:
                            discount_vals.append((0, 0, {
                                'min_amount': 0,
                                'max_amount': max_amount,
                                'discount': 1 - float(numbers[0])
                            }))
                    if discount_vals:
                        kho_data['discount_ids'] = discount_vals
            kho.append(kho_data)
        self.env['dth.kho.sim.maker'].create(kho)
    
    def process_old_data_phone_number(self, contact):
        contact1 = contact.replace(' ', '').replace('(', '').replace(')', '').replace('&', '-').replace('_', '-').replace(':', '-')
        new_contact = ''
        arr = []
        ct_arr = []
        if '-' in contact1:
            ct_arr = contact1.split('-')
        else:
            ct_arr.append(contact1)
        for ct in ct_arr:
            ct = ct.replace('.', '')
            if self.check_phone_number_format(ct) or self.check_hotline_format(ct):
                arr.append(ct)
            else:
                while (len(ct) > 10):
                    ct1 = ct[0:10]
                    if self.check_phone_number_format(ct1) or self.check_hotline_format(ct1):
                        arr.append(ct1)
                    ct = ct[10:]
        if arr:
            new_contact = '\n'.join(arr)
        else:
            contact2 = contact.replace(' ', '').replace('.', '')
            phone_pattern = re.compile(r'\b\d{10}\b')
            phone_numbers = phone_pattern.findall(contact2)
            new_contact = '\n'.join(phone_numbers)
        return new_contact
    
    def process_old_data_email(self, email):
        new_email = 'example@gmail.com'
        arr = []
        em_arr = []
        email = email.replace(' ', '-')
        if '-' in email:
            em_arr = email.split('-')
        else:
            em_arr.append(email)
        for em in em_arr:
            em = em.strip()
            if self.check_email_format(em):
                arr.append(em)
        if arr:
            new_email = '\n'.join(arr)
        return new_email

