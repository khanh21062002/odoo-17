from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    allow_sim_maker_ids = fields.Many2many('dth.kho.sim.maker', 'res_users_dth_sim_maker_allow_rel', 'user_id', 'sim_maker_id', string='Danh sách kho cho phép',
                                           compute='_compute_allow_sim_maker_ids', inverse='_inverse_allow_sim_maker_ids', store=True, readonly=False)
    not_allow_sim_maker_ids = fields.Many2many('dth.kho.sim.maker', 'res_users_dth_sim_maker_not_allow_rel', 'user_id', 'sim_maker_id', string='Danh sách kho không cho phép')
    
    @api.depends('not_allow_sim_maker_ids')
    def _compute_allow_sim_maker_ids(self):
        for r in self:
            sim_makers = self.env['dth.kho.sim.maker'].search([])
            allow_sim_maker_ids = sim_makers - self.env['dth.kho.sim.maker'].browse(r.not_allow_sim_maker_ids.ids).exists()
            r.allow_sim_maker_ids = allow_sim_maker_ids
    
    def _inverse_allow_sim_maker_ids(self):
        for r in self:
            sim_makers = self.env['dth.kho.sim.maker'].search([])
            r.not_allow_sim_maker_ids = sim_makers - r.allow_sim_maker_ids
    
    def clear_all_allow_list(self):
        self.write({'allow_sim_maker_ids': [(6, 0, [])]})
    
    def clear_all_not_allow_list(self):
        self.write({'not_allow_sim_maker_ids': [(6, 0, [])]})
    
    def write(self, vals):
        self.clear_caches()
        return super(ResUsers, self).write(vals)
