from odoo import models, fields, api

class ReportLowQualityNumbers(models.Model):
    _name = 'dth.kho.report.low.quality.numbers'
    _description = 'Báo cáo bảng số chất lượng thấp'
    _order = 'create_date desc'
    _auto = False

    sim_maker_id = fields.Many2one('dth.kho.sim.maker', string='Mã kho')
    create_date = fields.Datetime(string='Ngày up bảng', default=fields.Datetime.now)
    total_sim = fields.Integer(string='Số lượng sim')
    time_yet = fields.Integer(string='Thời gian up mới')
    loss_rate = fields.Float(string='Tỉ lệ mất số')
    committed_sim_rate = fields.Float(string='Tỉ lệ sim cam kết')
    rate_uploading_wrong_price = fields.Float(string='Tỉ lệ up sai giá')

    @api.model
    def _select(self):
        return '''
            WITH sim_data_warehouse AS (
                SELECT
                    dsw.sim_maker_id,
                    COUNT(CASE WHEN dsw.sim_status = 'da_ban' THEN 1 END) AS sold_count,
                    COUNT(dsw.sim_maker_id) AS total_sim,
                    COUNT(dsd.commited) AS total_commit
                FROM
                    dth_kho_sim_data dsd
                JOIN
                    dth_kho_sim_warehouse dsw ON dsw.sim_data_id = dsd.id
                GROUP BY
                    dsw.sim_maker_id
            ),
            latest_abnormal_sim AS (
                SELECT
                    dsuh.sim_maker_id,
                    dsuh.abnormal_sim,
                    dsuh.total_sim
                FROM
                    dth_kho_sim_upload_history dsuh
                INNER JOIN (
                    SELECT
                        sim_maker_id,
                        MAX(create_date) AS max_create_date
                    FROM
                        dth_kho_sim_upload_history
                    GROUP BY
                        sim_maker_id
                ) max_dsuh ON dsuh.sim_maker_id = max_dsuh.sim_maker_id AND dsuh.create_date = max_dsuh.max_create_date
            ),
            metrics AS (
                SELECT
                    ROW_NUMBER() OVER () AS id,
                    dsuh.sim_maker_id,
                    MAX(dsuh.create_date) AS create_date,
                    GREATEST(DATE_PART('day', CURRENT_DATE - MAX(dsuh.create_date)), 0) AS time_yet,
                    MAX(sdw.total_sim) AS total_sim,
                    CASE 
                        WHEN COALESCE(MAX(sdw.total_sim), 0) = 0 THEN 0
                        ELSE (COALESCE(MAX(sdw.sold_count), 0) / CAST(COALESCE(MAX(sdw.total_sim), 0) AS DECIMAL(10, 2)))
                    END AS loss_rate,
                    CASE 
                        WHEN COALESCE(MAX(sdw.total_sim), 0) = 0 THEN 0
                        ELSE (COALESCE(MAX(sdw.total_commit), 0) / CAST(COALESCE(MAX(sdw.total_sim), 0) AS DECIMAL(10, 2)))
                    END AS committed_sim_rate,
                    CASE 
                        WHEN COALESCE(MAX(la.total_sim), 0) = 0 THEN 0
                        ELSE (COALESCE(MAX(la.abnormal_sim), 0) / CAST(COALESCE(MAX(la.total_sim), 0) AS DECIMAL(10, 2)))
                    END AS rate_uploading_wrong_price
                FROM
                    dth_kho_sim_upload_history dsuh
                INNER JOIN
                    sim_data_warehouse sdw ON sdw.sim_maker_id = dsuh.sim_maker_id
                INNER JOIN
                    latest_abnormal_sim la ON la.sim_maker_id = dsuh.sim_maker_id
                WHERE dsuh.state = 'done'
                GROUP BY
                    dsuh.sim_maker_id
            )
            SELECT *
            FROM metrics
            WHERE committed_sim_rate >= 0.8 
                AND time_yet > 30 
                AND rate_uploading_wrong_price >= 0.1
            ORDER BY loss_rate DESC
            LIMIT 10
        '''

    @property
    def _table_query(self):
        return '%s' % (self._select())
