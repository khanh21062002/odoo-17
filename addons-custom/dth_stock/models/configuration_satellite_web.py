from odoo import models, fields, api

class SatelliteWebConfiguration(models.Model):
    _name = 'dth.kho.configuration.satellite.web'
    _description = 'Cấu hình web vệ tinh'
    _order = 'create_date desc'

    name = fields.Char(string='Tên DB', required=True)
    configuration_type = fields.Selection([
        ('white_list', 'Whitelist'),
        ('black_list', 'Blacklist'),
    ], string='Loại cấu hình', required=True)
    code_configuration_type = fields.Char(string='Mã kho loại cấu hình', help='Nếu Loại cấu hình là Whitelist thì nhập các mã kho bao gồm, nếu là Blacklist thì nhập các mã kho không bao gồm')
    information_sim = fields.Many2many('dth.kho.information.sim', string='Thông tin cần')
    configuration_repository_id = fields.One2many('dth.kho.configuration.satellite.web.line', 'configuration_id', string='Kho cấu hình')

class SatelliteWebConfigurationLine(models.Model):
    _name = 'dth.kho.configuration.satellite.web.line'
    _description = 'Cấu hình web vệ tinh'
    _order = 'create_date desc'

    configuration_id = fields.Many2one('dth.kho.configuration.satellite.web', string='Cấu hình')
    sim_maker_id = fields.Many2one('dth.kho.sim.maker', string='Thợ sim', required=True)
    priority_point = fields.Integer(string='Điểm ưu tiên', default=1000)
    promotion = fields.Char(string='Khuyến mại')
    present = fields.Char(string='Quà tặng')

class InformationSim(models.Model):
    _name = 'dth.kho.information.sim'
    _description = 'Thông tin số sim'
    _order = 'create_date desc'

    name = fields.Char(string='Tên thông tin', required=True)
    slug = fields.Char(string='Slug thông tin', required=True)