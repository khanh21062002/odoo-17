from odoo import models, fields, api

class SimNumberUploadHistory(models.Model):
    _name = 'dth.kho.sim.number.upload.history'
    _description = "Lịch sử up số sim"
    _order = "create_date desc"
    _auto = False

    sim_number = fields.Char(string='Số sim')
    sim_maker_id = fields.Many2one('dth.kho.sim.maker', string='Thợ sim')
    latest_upload_time = fields.Datetime(string='Thời gian up gần nhất')
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', default=lambda self: self.env.ref('base.VND'))
    min_selling_price = fields.Monetary(string='Giá bán min', currency_field='currency_id')
    max_selling_price = fields.Monetary(string='Giá bán max', currency_field='currency_id')
    min_collection_price = fields.Monetary(string='Giá thu min', currency_field='currency_id')
    max_collection_price = fields.Monetary(string='Giá thu max', currency_field='currency_id')
    create_date = fields.Datetime(string='Creation Date', default=fields.Datetime.now)
    # telecom_supplier_id = fields.Many2one('dth.telecom.supplier', string='Nhà mạng')

    @api.model
    def _select(self):
        return '''
            SELECT
                MIN(uhl.id) AS id, 
                uhl.sim_name AS sim_number, 
                MAX(uhl.create_date) AS latest_upload_time, 
                MIN(uhl.sell_price_s) AS min_selling_price, 
                MAX(uhl.sell_price_s) AS max_selling_price, 
                MIN(uhl.buy_price_s) AS min_collection_price, 
                MAX(uhl.buy_price_s) AS max_collection_price, 
                MAX(uhl.create_date) AS create_date,
                uh.sim_maker_id AS sim_maker_id,
                23 AS currency_id
        '''

    @api.model
    def _from(self):
        return '''
            FROM dth_kho_sim_upload_history_line as uhl
            INNER JOIN dth_kho_sim_upload_history as uh
            ON uhl.upload_history_id = uh.id
            WHERE uh.state = 'done'
            GROUP BY
                uh.sim_maker_id,
                uhl.sim_name
        '''

    @api.model
    def _where(self):
        return ''

    @api.model
    def _group_by(self):
        return ''

    def detail_upload_sim(self):
        if not self.sim_number:
            action = self.env.ref('dth_stock.action_sim_number_upload_history').sudo().read()[0]
        else:
            action = self.env.ref('dth_stock.action_sim_number_upload_history_detail').sudo().read()[0]
            action['context'] = {
                'default_sim_number': self.sim_number,  # Pass sim_number value
            }
        return action
    
    @property
    def _table_query(self):
        return '%s %s %s %s' % (self._select(), self._from(), self._where(), self._group_by())

class SimNumberUploadHistoryDetail(models.Model):
    _name = 'dth.kho.sim.number.upload.history.detail'
    _description = "Chi tiết lịch sử up số sim"
    _order = "create_date desc"
    _auto = False

    sim_number = fields.Char(string='Số sim')
    sim_maker_id = fields.Many2one('dth.kho.sim.maker', string='Thợ sim')
    buy_price_s = fields.Monetary(string='Giá thu', currency_field='currency_id')
    sell_price_s = fields.Monetary(string='Giá bán', currency_field='currency_id')
    create_date = fields.Datetime(string='Ngày tạo', default=fields.Datetime.now)
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', default=lambda self: self.env.ref('base.VND'))

    @api.model
    def _select(self):
        sim_number = self._context.get('default_sim_number', False)
        if sim_number:
            return f'''
                SELECT
                    row_number() over () as id,
                    dsuh.sim_maker_id as sim_maker_id,
                    dsuhl.sim_name as sim_number,
                    dsuhl.buy_price_s as buy_price_s,
                    dsuhl.sell_price_s as sell_price_s,
                    dsuhl.create_date as create_date,
                    23 as currency_id
                FROM dth_kho_sim_upload_history_line dsuhl
                INNER JOIN dth_kho_sim_upload_history dsuh ON dsuhl.upload_history_id = dsuh.id
                WHERE dsuhl.sim_name = '{sim_number}'
            '''
        else:
            return '''
                SELECT
                    row_number() over () as id,
                    dsuh.sim_maker_id as sim_maker_id,
                    dsuhl.sim_name as sim_number,
                    dsuhl.buy_price_s as buy_price_s,
                    dsuhl.sell_price_s as sell_price_s,
                    dsuhl.create_date as create_date,
                    23 as currency_id
                FROM dth_kho_sim_upload_history_line dsuhl
                INNER JOIN dth_kho_sim_upload_history dsuh ON dsuhl.upload_history_id = dsuh.id
            '''

    @property
    def _table_query(self):
        return self._select()