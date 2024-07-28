import xlsxwriter
from io import BytesIO
import base64
import json

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
from confluent_kafka import Producer
from kafka import KafkaProducer

class SimUploadHistory(models.Model):
    _name = 'dth.kho.sim.upload.history'
    _inherit = ['mail.thread']
    _description = 'Lịch sử Up sim'
    _order = 'create_date desc'

    sim_maker_id = fields.Many2one('dth.kho.sim.maker', string='Thợ sim', index=True)
    type = fields.Selection([('manual', 'Thủ công'), ('auto', 'Tự động')], default="manual", string='Hình thức')
    state = fields.Selection([('draft', 'Nháp'),
                              ('to_confirm', 'Chờ duyệt'), 
                              ('processing', 'Đang xử lý'), 
                              ('done', 'Hoàn thành'), 
                              ('cancel', 'Hủy')], string='Trạng thái', default='draft')
    total_sim = fields.Integer(string='Tổng số sim', compute='_compute_total_sim', store=True)
    abnormal_sim = fields.Integer(string='Bất thường', compute='_compute_abnormal_sim', store=True)
    old_sim = fields.Integer(string='Số sim cũ')
    new_sim = fields.Integer(string='Số sim mới')
    sold_sim = fields.Integer(string='Số đã bán')
    confirm_user_id = fields.Many2one('res.users', string='Người xác nhận')
    confirm_date = fields.Datetime(string='Ngày hoàn thành')
    line_ids = fields.One2many('dth.kho.sim.upload.history.line', 'upload_history_id', string='Chi tiết')
    line_store_ids = fields.One2many('dth.kho.sim.upload.history.line.store', 'upload_history_id', string='Chi tiết lưu trữ')
    file_upload = fields.Binary(string='Bảng số', required=True)
    file_name = fields.Char(string='Tên File')
    file_upload_temp = fields.Binary(string='Bảng số Temp', attachment=False)
    email = fields.Char(string='Email')
    sim_maker_id_domain = fields.Binary(compute="_compute_sim_maker_id_domain", string='Domain thợ sim')
    
    @api.constrains('sim_maker_id')
    def _check_sim_maker_id(self):
        for r in self:
            if r.sim_maker_id and r.email:
               sim_maker = self.env['dth.kho.sim.maker'].search([('id', '=', r.sim_maker_id.id), ('email', 'ilike', r.email)], limit=1) 
               if not sim_maker:
                    raise ValidationError('Email và thợ sim không trùng khớp, vui lòng chọn thợ sim chính xác.')
    
    @api.onchange('file_upload')
    def _onchange_file_upload(self):
        if self.file_upload:
            file_name = self.file_name
            if not file_name.endswith('.xls') and not file_name.endswith('.xlsx'):
                raise ValidationError("File phải là định dạng 'xlsx' hoặc 'xls'")
    
    @api.depends('email')
    def _compute_sim_maker_id_domain(self):
        for r in self:
            domain = []
            if r.email:
                domain = [('email', 'ilike', r.email)]
            r.sim_maker_id_domain = domain
    
    @api.depends('line_ids')
    def _compute_total_sim(self):
        for r in self:
            r.total_sim = len(r.line_ids)
            
    @api.depends('line_ids.abnormal')
    def _compute_abnormal_sim(self):
        for r in self:
            r.abnormal_sim = len(r.line_ids.filtered(lambda l: l.abnormal))
    
    # @api.depends('line_ids.sim_name', 'sim_maker_id')
    # def _compute_number_sim(self):
    #     for r in self:
    #         if r.line_ids and r.sim_maker_id:
    #             r.total_sim = len(r.line_ids)
    #             new_sims = r.line_ids.filtered(lambda l: l.sim_name and (l.sim_name.replace('.', '') in r.sim_maker_id.sim_warehouse_ids.filtered(lambda sw: sw.sim_status == 'da_ban').mapped('name') 
    #                                            or l.sim_name.replace('.', '') not in r.sim_maker_id.sim_warehouse_ids.mapped('name')))
    #             old_sims = r.line_ids.filtered(lambda l: l.sim_name and l.sim_name.replace('.', '') in r.sim_maker_id.sim_warehouse_ids.filtered(lambda sw: sw.sim_status == 'so_con').mapped('name'))
    #             new_names = [line.sim_name.replace('.', '') for line in r.line_ids.filtered(lambda l: l.sim_name)]
    #             sold_sims = r.sim_maker_id.sim_warehouse_ids.filtered(lambda wh: wh.sim_status == 'so_con' and wh.name not in new_names)
    #             r.old_sim = len(old_sims)
    #             r.new_sim = len(new_sims)
    #             r.sold_sim = len(sold_sims)
    #         else:
    #             r.total_sim = 0
    #             r.old_sim = 0
    #             r.new_sim = 0
    #             r.sold_sim = 0
            
    @api.depends('sim_maker_id')
    def _compute_display_name(self):
        for r in self:
            if r.sim_maker_id and r.create_date:
                r.display_name = f"{r.sim_maker_id.display_name} ({r.create_date.date().strftime('%d-%m-%Y')})"
            else:
                r.display_name = ''
    
    def upload_file(self):
        url = self.env['ir.config_parameter'].sudo().get_param('url_api_up_file', 'http://192.168.0.171:8000/trigger_task')
        data = {
                'file_data': self.file_upload.decode("utf-8"), 
                'file_name': self.file_name, 
                'history_id': str(self.id),
                'sim_maker_id': [str(self.sim_maker_id.id)],
                'user_id': str(self.env.user.id),
                }
        file = requests.request('POST', url, data=json.dumps(data))
        result = file.json()    
        if result.get('message', '') == 'DAG triggered successfully':
            self.state = 'processing'
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'message': 'Up bảng thành công, vui lòng chờ hệ thống xử lý dữ liệu.',
                    'next': {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    },
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'message': result.get('message', 'File không hợp lệ.'),
                    'next': {
                        'type': 'ir.actions.act_window_close'
                    },
                }
            }
    
    def process_message(self, message):
        with self.pool.cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr))
            root = self.env['ir.model.data']._xmlid_to_res_id("base.partner_root")
            users = self.env.company.upload_sim_noti_user_ids
            if users:
                for r in self:
                    r.with_user(1).message_post(
                            body=message,
                            author_id=root,
                            partner_ids=users.partner_id.ids
                        )
    
    def approve_upload(self):
        data = {
            'history_id': self.id,
            'message': 'Sim upload history approved!'
            }
        url_kafka_bootstrap_servers = self.env['ir.config_parameter'].sudo().get_param('url_kafka_bootstrap_servers', '192.168.0.171:29092')
        producer = KafkaProducer(bootstrap_servers=url_kafka_bootstrap_servers, api_version=(2, 2, 0))
    
        # Send data to Kafka topic
        producer.send('approve_topic', json.dumps(data).encode('utf-8'))
        producer.flush()
        self.state = 'processing'
        self.confirm_date = fields.Datetime.now()
        
        return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'message': 'Duyệt bảng số thành công, vui lòng chờ hệ thống xử lý và làm giàu giữ liệu.',
                    'next': {
                        'type': 'ir.actions.act_window_close'
                    },
                }
            }
    
    def get_data(self):
        data = []
        stt = 1
        abnormal_lines = self.line_ids.filtered(lambda l: l.abnormal)
        for rec in abnormal_lines:
            val = [
                stt,
                rec.sim_name or '',
                rec.sell_price_s or 0,
                rec.buy_price_s or 0,
                rec.note or '',
            ]
            data.append(val)
            stt += 1
        return data
    
    def download_abnormal(self):
        datas = self.get_data()
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        worksheet = workbook.add_worksheet()
        worksheet.set_landscape()
        worksheet.fit_to_pages(1, 0)
        
        worksheet.set_column(0, 0, 5)#STT
        worksheet.set_column(1, 1, 20)#Số sim
        worksheet.set_column(2, 2, 20)#Giá bán
        worksheet.set_column(3, 3, 20)#Giá thu
        worksheet.set_column(4, 4, 35)#Ghi chú
        
        name_style_format = workbook.add_format({'bold': True,
                                           'bottom': 1,
                                           'align':'center',
                                           'valign': 'vcenter',
                                           'text_wrap': True,
                                           'border': 1,
                                           'font_name': 'Times New Roman',
                                           'font_size': 13})
        
        worksheet.write(0, 0, 'STT', name_style_format)
        worksheet.write(0, 1, 'Số sim', name_style_format)
        worksheet.write(0, 2, 'Giá bán', name_style_format)
        worksheet.write(0, 3, 'Giá thu', name_style_format)
        worksheet.write(0, 4, 'Ghi chú', name_style_format)
        
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
        wizard = self.env['sim.upload.history.download.wizard'].create({'data': out})
        
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/sim.upload.history.download.wizard/%s/%s/%s' % (
                wizard.id, 'data', '%s_batthuong' % self.sim_maker_id.display_name),
            'target': 'new',
        }
    
    def transfer_temp_file(self):
        temp_file_histories = self.env['dth.kho.sim.upload.history'].search([('file_upload_temp', '!=', False)])
        for history in temp_file_histories:
            history.file_upload = history.file_upload_temp
            history.file_upload_temp = False
    
    @api.onchange('sim_maker_id')
    def _onchange_sim_maker_id(self):
        if self.state == 'to_confirm' and self.sim_maker_id:
            url = self.env['ir.config_parameter'].sudo().get_param('url_api_calculates_collection_price', 'http://192.168.0.171:8000/trigger_update_buy_price')
            data = {
                    'sim_maker_id': str(self.sim_maker_id.id), 
                    'history_id': str(self._origin.id)
                    }
            file = requests.request('POST', url, data=json.dumps(data))
            result = file.json()
            if result.get('message', '') == 'Update buy_price successfully':
                self.write({'sim_maker_id': self.sim_maker_id.id})
            else:
                raise ValidationError('Có lỗi xảy ra khi tính toán lại giá thu theo thợ sim, vui lòng liên hệ quản trị hệ thống.')
    
    def write(self, vals):
        res = super(SimUploadHistory, self).write(vals)
        if 'line_ids' in vals:
            line_ids = []
            for line in self.line_ids.filtered(lambda l: l.abnormal):
                if line.check_abnormal():
                    line_ids.append(line.id)
            if line_ids:
                self.env.cr.execute("""UPDATE dth_kho_sim_upload_history_line SET abnormal = false WHERE id in (%s)""" % (",".join(line_ids),))
        return res
