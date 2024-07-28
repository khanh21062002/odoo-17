from odoo import models, fields, api

class SimSearchHistory(models.Model):
    _name = 'dth.kho.sim.search.history'
    _description = "Lịch sử tra số"
    _order = 'create_date desc, id desc'

    sim_search = fields.Char(string='Số sim', index=True)
