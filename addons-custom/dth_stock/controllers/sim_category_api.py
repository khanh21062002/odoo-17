from datetime import datetime
from dateutil.relativedelta import relativedelta
import math
import logging
_logger = logging.getLogger(__name__)

from odoo import http, _
from odoo.exceptions import UserError, ValidationError,AccessError
from odoo.http import request
from odoo.osv import expression
from .main import error_response, successful_response

class SimCategory(http.Controller):
    @http.route('/api/sim_category/get_sim_category',
                methods=['POST'],
                type='http',
                auth='none',
                cors='*',
                csrf=False)

    def get_sim_category(self, **kw):
        try:
            domain = []
            sim_category = request.env['dth.kho.sim.category'].sudo().search_read(domain, fields=['code', 'name', 'sequence'], order='sequence asc')
            result = {
                "data": sim_category
            }
            return successful_response(status=200, data=result, success_code='success',
                                       message=_("Lấy dữ liệu thành công"))
        except AccessError as a:
            _logger.error(str(a))
            return error_response(status=401,
                                  error_code=_("access_error"),
                                  message=_("Bạn không có quyền truy cập dữ liệu này"), data={})

        except ValueError as v:
            error_descrip = _("Wrong input format!")
            _logger.error(str(v))
            return error_response(status=400, error_code='value_error', message=error_descrip)

        except Exception as a:
            _logger.error(str(a))
            return error_response(status=500,
                                  error_code=_("exception_error"),
                                  message=_("Đã có lỗi xảy ra. Vui lòng liên hệ quản trị hệ thống."), data={})