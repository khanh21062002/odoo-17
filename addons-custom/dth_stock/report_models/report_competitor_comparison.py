from odoo import models, fields, api

class ReportCompetitorComparison(models.Model):
    _name = 'dth.kho.report.competitor.comparison'
    _description = 'Báo cáo so sánh đối thủ'
    _order = 'create_date desc'
    _auto = False

    sim_maker_id = fields.Many2one('dth.kho.sim.maker', string='Mã kho')
    create_date = fields.Datetime(string='Create Date', default=fields.Datetime.now)
    telecom_supplier_id = fields.Many2one('dth.kho.telecom.supplier', string='Nhà mạng', ondelete='restrict')
    telecom_supplier_code = fields.Integer(string="Mã nhà mạng", store=True, index=True)
    price_range = fields.Selection([
        ('0-500000', 'Giá dưới 500k'), 
        ('500000-1000000', '500 - 1 Triệu'),
        ('1000000-3000000', '1 - 3 Triệu'),
        ('3000000-5000000', '3 - 5 Triệu'),
        ('5000000-10000000', '5 - 10 Triệu'),
        ('10000000-30000000', '10 - 30 Triệu'),
        ('30000000-50000000', '30 - 50 Triệu'),
        ('50000000-80000000', '50 - 80 Triệu'),
        ('80000000-100000000', '80 - 100 Triệu'),
        ('100000000-150000000', '100 - 150 Triệu'),
        ('150000000-200000000', '150 - 200 Triệu'),
        ('200000000-300000000', '200 - 300 Triệu'),
        ('300000000-500000000', '300 - 500 Triệu'),
        ('500000000-1000000000', '500 Triệu - 1 Tỷ'),
        ('1000000000-10000000000000', 'Trên 1 Tỷ'),
    ], string='Khoảng giá')
    category_ids = fields.Many2one('dth.kho.sim.category', string='Loại sim', ondelete='restrict')
    sim_count = fields.Integer(string='Số lượng sim')
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', default=lambda self: self.env.ref('base.VND'))
    avg_price = fields.Float(string='Giá bán trung bình', currency_field='currency_id')

    @api.model
    def _select(self):
        return '''
            SELECT
                row_number() OVER () AS id,
                sw.sim_maker_id,
                MAX(sw.write_date) AS create_date,
                sd.telecom_supplier_id as telecom_supplier_id,
                MAX(sd.telecom_supplier_code) as telecom_supplier_code,
                scdsd.dth_sim_category_id AS category_ids,
                AVG(sw.sell_price_s) AS avg_price,
                23 AS currency_id,
                CASE 
                    WHEN sw.sell_price_s BETWEEN 0 AND 499999 THEN '0-500000'
                    WHEN sw.sell_price_s BETWEEN 500000 AND 1000000 THEN '500000-1000000'
                    WHEN sw.sell_price_s BETWEEN 1000000 AND 3000000 THEN '1000000-3000000'
                    WHEN sw.sell_price_s BETWEEN 3000000 AND 5000000 THEN '3000000-5000000'
                    WHEN sw.sell_price_s BETWEEN 5000000 AND 10000000 THEN '5000000-10000000'
                    WHEN sw.sell_price_s BETWEEN 10000000 AND 30000000 THEN '10000000-30000000'
                    WHEN sw.sell_price_s BETWEEN 30000000 AND 50000000 THEN '30000000-50000000'
                    WHEN sw.sell_price_s BETWEEN 50000000 AND 80000000 THEN '50000000-80000000'
                    WHEN sw.sell_price_s BETWEEN 80000000 AND 100000000 THEN '80000000-100000000'
                    WHEN sw.sell_price_s BETWEEN 100000000 AND 150000000 THEN '100000000-150000000'
                    WHEN sw.sell_price_s BETWEEN 150000000 AND 200000000 THEN '150000000-200000000'
                    WHEN sw.sell_price_s BETWEEN 200000000 AND 300000000 THEN '200000000-300000000'
                    WHEN sw.sell_price_s BETWEEN 300000000 AND 500000000 THEN '300000000-500000000'
                    WHEN sw.sell_price_s BETWEEN 500000000 AND 1000000000 THEN '500000000-1000000000'
                    WHEN sw.sell_price_s BETWEEN 1000000000 AND 10000000000000 THEN '1000000000-10000000000000'
                    ELSE '0-500000'
                END AS price_range,
                COUNT(*) AS sim_count
    '''

    @api.model
    def _from(self):
        return '''
            FROM 
                dth_kho_sim_warehouse sw
            INNER JOIN 
                dth_kho_sim_data sd ON sw.sim_data_id = sd.id
            INNER JOIN 
                dth_sim_category_dth_kho_sim_data_rel scdsd ON sd.id = scdsd.dth_kho_sim_data_id
            GROUP BY
                sw.sim_maker_id,
                sd.telecom_supplier_id,
                scdsd.dth_sim_category_id,
                price_range
    '''

    @property
    def _table_query(self):
        return '%s %s' % (self._select(), self._from())
