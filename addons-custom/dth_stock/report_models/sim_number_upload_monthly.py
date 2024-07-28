from odoo import models, fields, api

class SimNumberUploadMonthly(models.Model):
    _name = 'dth.kho.sim.number.upload.monthly'
    _description = "Số lượng sim up hàng tháng"
    _order = "create_date desc"
    _auto = False

    sim_maker_id = fields.Many2one('dth.kho.sim.maker', string='Thợ sim')
    upload_time = fields.Datetime(string='Ngày up bảng')
    total_sim = fields.Integer(string='Số lượng sim')
    sold_sim = fields.Integer(string='Số sim đã bán')
    new_sim = fields.Integer(string='Số sim up mới')
    percent_error = fields.Float(string='Tỉ lệ up sai', group_operator="avg")
    create_date = fields.Datetime(string='Creation Date', default=fields.Datetime.now)

    @api.model
    def _select(self):
        return '''
            SELECT
                uh.id AS id,
                uh.sim_maker_id AS sim_maker_id,
                uh.create_date AS upload_time,
                greatest(uh.total_sim, 0) AS total_sim,
                greatest(uh.sold_sim, 0) AS sold_sim,
                greatest(uh.new_sim, 0) AS new_sim,
                CASE 
                    WHEN COALESCE(uh.total_sim, 0) = 0 THEN 0
                    ELSE (COALESCE(uh.abnormal_sim, 0) / CAST(COALESCE(uh.total_sim, 0) AS DECIMAL(10,2)))
                END AS percent_error,
                uh.create_date AS create_date
        '''

    @api.model
    def _from(self):
        return '''
            FROM dth_kho_sim_upload_history AS uh
        '''

    @api.model
    def _where(self):
        return '''
            WHERE uh.state = 'done'
        '''

    @api.model
    def _group_by(self):
        return ''

    @property
    def _table_query(self):
        return '%s %s %s %s' % (self._select(), self._from(), self._where(), self._group_by())