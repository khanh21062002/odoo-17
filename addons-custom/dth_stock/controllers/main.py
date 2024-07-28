from odoo import http
from odoo.http import request
import json
import werkzeug.wrappers
from odoo.tools import date_utils

def successful_response(status, data, success_code='success', message=''):
    resp = werkzeug.wrappers.Response(
        status=status,
        content_type='application/json; charset=utf-8',
        #headers = None,
        response=json.dumps({
            'status': success_code,
            'data': data,
            'message': message,
        }, ensure_ascii=False, default=date_utils.json_default),
    )
    # Remove cookie session
    resp.set_cookie = lambda *args, **kwargs: None
    return resp


def error_response(status, error_code, message, data={}):
    resp = werkzeug.wrappers.Response(
        status=status,
        content_type='application/json; charset=utf-8',
        #headers = None,
        response=json.dumps({
            'status': error_code,
            'data': data,
            'message': message,
        }, ensure_ascii=False),
    )
    # Remove cookie session
    resp.set_cookie = lambda *args, **kwargs: None
    request.env.cr.rollback()
    return resp

class StockController(http.Controller):

    def _check_token(self, token):
        # Function to check if the token is valid
        valid_token = 'your_secret_token_here'  # Replace this with your actual token validation logic
        return token == valid_token

    @http.route('/api/data', type='json', auth='none', methods=['POST'], csrf=False)
    def get_data(self, **kwargs):
        token = request.httprequest.headers.get('Authorization')
        if not self._check_token(token):
            return json.dumps({'error': 'Unauthorized'}), 401
        
        # Fetch data from Odoo models
        data = request.env['res.partner'].sudo().search_read([], ['name', 'email'])
        return json.dumps({'data': data})
    
    @http.route('/sim_warehouse_spa/', auth='user', website=False)
    def index(self, **kw):
        response = http.request.render('dth_stock.sim_warehouse_spa', {})
        if http.request.session.uid:
            response.set_cookie('user_id', str(http.request.session.uid), secure=True, samesite='Lax')
        return response 
    
