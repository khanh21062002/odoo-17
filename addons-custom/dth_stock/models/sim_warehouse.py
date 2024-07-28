from odoo import models, fields, api
from odoo.exceptions import ValidationError
import pytz

class SimWarehouse(models.Model):
    _name = 'dth.kho.sim.warehouse'
    _inherits = {'dth.kho.sim.data': 'sim_data_id'}
    _inherit = ['mail.thread']
    _description = 'Số sim theo kho'
    _display_name = 'name_full'
    _order = 'sim_data_id, write_date desc'
    
    sim_data_id = fields.Many2one('dth.kho.sim.data', string='Số sim chính', auto_join=True, index=True, ondelete="cascade")
    sim_maker_id = fields.Many2one('dth.kho.sim.maker', string='Kho', required=True, index=True)
    sim_maker_code = fields.Char(related='sim_maker_id.code', store=True, string='Mã kho', index=True) #id
    sell_price_s = fields.Monetary(string='Giá bán', currency_field='currency_id', group_operator=False, tracking=True) #pb
    buy_price_s = fields.Monetary(string='Giá thu', currency_field='currency_id', group_operator=False, tracking=True) #pn
    profit = fields.Monetary(string='Lợi nhuận', currency_field='currency_id', compute='_compute_profit', store=True)
    sim_status = fields.Selection([('dang_lv', 'Đang làm việc'), ('so_con', 'Số còn'), ('da_ban', 'Đã bán')], index=True, default="so_con", string='Trạng thái', tracking=True)
    priority_by_sm = fields.Integer(string='Điểm ưu tiên theo kho')
    installment = fields.Boolean(string='Cho phép trả góp', related='sim_maker_id.installment', store=True)
    installment_percent = fields.Float(string='Trả góp')
    sm_description = fields.Html(string='Thông tin kho', compute='_compute_sm_description', help="Kho", compute_sudo=True)
    # status_color = fields.Char(string='Màu sắc', compute='_compute_status_color')
    comment_display = fields.Html(string="Comment hiệu lực", compute='_compute_comment_display', help="Số sim", compute_sudo=True)
    comment_wh_history_ids = fields.One2many('dth.kho.comment.history', compute='_compute_comment_wh_history_ids')
    
    _sql_constraints = [('sim_data_id_sim_maker_uniq', "unique(sim_data_id, sim_maker_id)", "Số sim đã tồn tại trong kho.")]
    
    def _compute_comment_wh_history_ids(self):
        for r in self:
            r.comment_wh_history_ids = r.comment_history_ids.filtered(lambda c: c.apply_all or c.sim_warehouse_id.id == r.id)
    
    @api.depends('name_full')
    def _compute_display_name(self):
        for r in self:
            r.display_name = r.name_full
    
    @api.depends('web_price_s', 'buy_price_s')
    def _compute_profit(self):
        for r in self:
            if r.web_price_s and r.buy_price_s:
                r.profit = r.web_price_s - r.buy_price_s
            else:
                r.profit = 0
    
    def _compute_comment_display(self):
        for r in self:
            last_comment = r.comment_history_ids.filtered(lambda c: c.apply_all)
            if r.sim_status == 'da_ban' or r.sim_maker_id.peel_wh:
                comment = '<div style="font-size: 16px; padding-bottom: 5px; max-width: 200px; text-decoration: line-through;">' + r.name_full + '</div>'
            else:
                comment = '<div style="font-size: 16px; padding-bottom: 5px; max-width: 200px; color: #339900;">' + r.name_full + '</div>'
            if last_comment:
                create_date = last_comment[0].create_date.astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))
                comment += '<div style="color: #ff2f2f; font-size: 12px; max-width: 200px"><strong>%s</strong> (%s)</div>' % (last_comment[0].create_uid.name, create_date.strftime('%H:%M %d/%m'))
                comment += '<div style="color: #ff2f2f; font-size: 12px; max-width: 200px; white-space: break-spaces">%s - %s</div>' %  (last_comment[0].state, last_comment[0].comment_note)
            r.comment_display = comment
            
    def _compute_status_color(self):
        for r in self:
            if r.sim_status == 'dang_lv':
                r.status_color = '#55ffff'
            elif r.sim_status == 'so_con':
                r.status_color = '#45B26B'
            elif r.sim_status == 'da_ban':
                r.status_color = '#a8aaa8'
            else:
                r.status_color = ''
    
    def _compute_sm_description(self):
        for r in self:
            r.sm_description = ''
            if r.sim_maker_id:
                sim_maker = r.sim_maker_id
                des = '<div>'
                if sim_maker.priority_wh:
                    des += '<img src="/dth_stock/static/img/vector.png" alt="Ưu tiên"/> '
                if sim_maker.monopoly_wh:
                    des += '<img src="/dth_stock/static/img/diamond.png" alt="Độc quyền"/> '
                if sim_maker.dth_wh:
                    des += '<strong><span style="color: #2264E5">(' + sim_maker.code + ') ' + sim_maker.name + '</span><strong>'
                else:
                    des += '<strong><span>(' + sim_maker.code + ') ' + sim_maker.name + '</span></strong>'
                # des += '<span style="color: #777E90"> (' + str(sim_maker.total_rating) + ' <img src="/dth_stock/static/img/star.png" alt="Đánh giá"/>)</span>'
                des += '</div>'
                des += '<div><span style="color: #777E90">'
                phone_numbers = sim_maker.phone_number.split('\n')
                if '' in phone_numbers:
                    phone_numbers.remove('')
                emails = sim_maker.email.split('\n')
                if '' in emails:
                    emails.remove('')
                des += ' - '.join(phone_numbers) + ' - ' + ' - '.join(emails)
                des += '</span></div>'
                if sim_maker.note:
                    des += '<div style="color: #ff2f2f; white-space: break-spaces">'+ sim_maker.note.replace('\n', '<br>').upper() +'</div>'
            r.sm_description = des
    
    @api.onchange('name_full')
    def _onchange_name_full(self):
        if self.name_full:
            name = self.name_full.replace('.', '')
            sim_data = self.env['dth.kho.sim.data'].search([('name', '=', name)], limit=1)
            if sim_data:
                self.sim_data_id = sim_data
    
    @api.model
    def fields_get(self, allfields=None, attributes=None):
        alow_list = ['web_price_s','sell_price_s','buy_price_s']
        res = super(SimWarehouse, self).fields_get(allfields, attributes)
        for key, value in res.items():
            if key not in alow_list:
                res[key]['searchable'] = False
        return res
    
    def unlink(self):
        for r in self:
            if r.sim_status == 'dang_lv':
                raise ValidationError("Không thể xóa sổ sim %s khi đang ở trạng thái đang làm việc." % r.name_full)
        return super(SimWarehouse, self).unlink()
            
    def change_status_sim(self):
        action = self.env.ref('dth_stock.change_status_sim_wizard_action').sudo().read()[0]
        return action
    
    def copy_sim(self):
        sim_warehouses = self.env['dth.kho.sim.warehouse'].browse(self.env.context.get('active_ids', [])).exists()
        if not sim_warehouses:
            sim_warehouses = self
        content = ''
        for sim_data in sim_warehouses.sim_data_id:
            content += '%s  %s\n' % (sim_data.name_full, self.env.ref('base.VND').format(sim_data.web_price_s))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_copy_board',
            'params': {
                'content': content
                },
            }
    
    def create(self, vals):
        if vals.get('sim_data_id', False):
            sim_data = self.env['dth.kho.sim.data'].browse(vals.get('sim_data_id', False)).exists()
            if sim_data:
                comment_histories = sim_data.sim_warehouse_ids.comment_history_ids.filtered(lambda c: c.comment_type == 'giu_so')
                if comment_histories:
                    vals['comment_history_ids'] = [(6, 0, comment_histories.ids)]
        return super(SimWarehouse, self).create(vals)
        
    
