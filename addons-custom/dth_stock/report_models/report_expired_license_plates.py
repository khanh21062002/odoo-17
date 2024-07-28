from odoo import models, fields, api

class ReportExpiredLicensePlates(models.Model):
    _name = 'dth.kho.report.expired.license.plates'
    _description = 'Báo cáo bảng số quá hạn'
    _order = 'create_date desc'
    _auto = False

    sim_maker_id = fields.Many2one('dth.kho.sim.maker', string='Mã kho')
    create_date = fields.Datetime(string='', default=fields.Datetime.now)
    time_updated_yet = fields.Integer(string='Thời gian chưa up mới')
    exceed_30_days = fields.Integer(string='Quá 30 ngày')
    exceed_61_days = fields.Integer(string='Quá 61 ngày')

    @api.model
    def _select(self):
        return '''
            SELECT
                MAX(uh.id) AS id,
                uh.sim_maker_id AS sim_maker_id,
                MAX(uh.create_date) AS create_date,
                GREATEST(DATE_PART('day', CURRENT_DATE - MAX(uh.create_date)), 0) AS time_updated_yet,
                GREATEST((DATE_PART('day', CURRENT_DATE - MAX(uh.create_date)) - 30), 0) AS exceed_30_days,
                GREATEST((DATE_PART('day', CURRENT_DATE - MAX(uh.create_date)) - 61), 0) AS exceed_61_days
        '''

    @api.model
    def _from(self):
        return '''
            FROM dth_kho_sim_upload_history AS uh
            WHERE uh.state = 'done'
            GROUP BY
                uh.sim_maker_id
            HAVING
                MAX(uh.create_date) <= (CURRENT_DATE - INTERVAL '30 days')
        '''

    @property
    def _table_query(self):
        return '%s %s' % (self._select(), self._from())