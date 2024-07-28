from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class PackageEndown(models.Model):
    _name = 'dth.kho.package.endown'
    _description = 'Ưu đãi'
    _order = 'date_end desc'

    package_id = fields.Many2one('dth.kho.mobile.package', string='Gói cước', ondelete='cascade')
    hot = fields.Boolean(string='Hot', default=False)
    description = fields.Text(string='Ưu đãi', required=True)
    date_start = fields.Date(string='Ngày bắt đầu')
    date_end = fields.Date(string='Ngày kết thúc')
    is_active = fields.Boolean(string='Còn hiệu lực', compute='_compute_is_active')
    
    @api.constrains('date_start', 'date_end')
    def _check_date_start_date_end(self):
        for r in self:
            if r.date_start and r.date_end and r.date_start > r.date_end:
                raise ValidationError("Ngày kết thúc ưu đãi phải sau ngày bắt đầu ưu đãi.")
    
    def _compute_is_active(self):
        today = fields.Date.today()
        for r in self:
            r.is_active = True
            if r.date_start and r.date_start > today:
                r.is_active = False
            if r.date_end and r.date_end < today:
                r.is_active = False
