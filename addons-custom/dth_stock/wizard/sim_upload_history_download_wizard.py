# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SimUploadHistoryDownloadWizard(models.TransientModel):
    _name = 'sim.upload.history.download.wizard'
    _description = 'Wizard download danh sách bất thường'

    data = fields.Binary(string='Data')
