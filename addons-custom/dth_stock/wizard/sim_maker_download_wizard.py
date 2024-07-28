# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SimMakerDownloadWizard(models.TransientModel):
    _name = 'sim.maker.download.wizard'
    _description = 'Wizard download thợ sim'

    data = fields.Binary(string='Data')
