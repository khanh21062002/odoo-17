from odoo.addons.web.controllers.home import Home
from odoo import http
from odoo.http import request

class Home(Home):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None):
        response = super(Home, self).web_client(s_action)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
