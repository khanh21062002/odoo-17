from datetime import datetime
from dateutil.relativedelta import relativedelta
import math
import json
import logging
_logger = logging.getLogger(__name__)

from odoo import http, _
from odoo.exceptions import UserError, ValidationError,AccessError
from odoo.http import request
from odoo.osv import expression
from .main import error_response, successful_response

class CommentHistory(http.Controller):
    @http.route('/api/comment_history/get_list_comment_history',
                methods=['POST'],
                type='http',
                auth='none',
                cors='*',
                csrf=False)
    
    def get_list_comment_history(self, **kw):
        try:
            user_id = kw.get('user_id', False)
            limit = kw.get('limit', 0)
            page = kw.get('page', 0)
            limit = int(limit)
            page = int(page)

            domain = []
            total_records = request.env['dth.kho.comment.history'].with_user(user_id).search_count(domain)
            
            if kw.get('sim_name', False):
                key_word = kw.get('sim_name').strip().replace('.', '')
                domain = expression.AND([domain, [('sim_data_id.name', 'ilike', key_word)]])
            if kw.get('user_name', False):
                key_word = kw.get('user_name').strip().replace('.', '')
                domain = expression.AND([domain, [('create_uid.partner_id.name', 'ilike', key_word)]])
            
            last_page = math.ceil(total_records/limit) or 1
            offset = 0 if limit * (page - 1) < 0 else limit * (page - 1)

            data = []
            comment_history = request.env['dth.kho.comment.history'].with_user(user_id).search_read(domain, fields=['id'], limit=limit, offset=offset)
            if comment_history:
                sql = """
                    SELECT 
                        dsd.name AS sim_name,
                        dch.create_date,
                        dch.state,
                        dch.note,
                        rp.name
                    FROM dth_comment_history dch
                    JOIN dth_kho_sim_data dsd ON dch.sim_data_id = dsd.id 
                    JOIN res_users ru  ON dch.create_uid = ru.id 
                    JOIN res_partner rp ON ru.partner_id = rp.id 
                    WHERE dch.id IN (%s)
                    ORDER BY dch.create_date DESC
                """ % (",".join([str(item['id']) for item in comment_history]),)
                request.env.cr.execute(sql)
                data = request.env.cr.dictfetchall() 
            result = {
                "total_page": last_page,
                "page": page,
                "records_of_page": limit,
                "total_records": total_records,
                "data": data
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

    @http.route('/api/comment_history/create_comment_history',
            type='http',
            auth='none',
            methods=['POST'],
            cors='*',
            csrf=False)
    def create_comment_history(self, **kw):
        try:
            if request.httprequest.content_type == 'application/json':
                data = request.jsonrequest if hasattr(request, 'jsonrequest') else json.loads(request.httprequest.data)
            else:
                data = kw
            
            user_id = data.get('user_id', False)
            sim_warehouse_id = data.get('sim_warehouse_id', False)
            state_value = data.get('state', False)
            note = data.get('note')
            apply_all = data.get('apply_all', False)

            partner = request.env['dth.kho.sim.warehouse'].with_user(user_id).browse(sim_warehouse_id)
            sim_data_id = partner.sim_data_id.id
        
            if not user_id or not sim_warehouse_id:
                return error_response(status=400, error_code='bad_request', message=_("Thiếu thông tin người dùng hoặc id số điện thoại"), data={})
            if not partner:
                return error_response(status=400, error_code='bad_request', message=_("Không tìm thấy thông tin kho"), data={})
            
            if state_value:
                if state_value == 'so_con':
                    state = 'Số còn'
                    sim_state = 'so_con'
                elif state_value == 'da_ban_co_chuong':
                    state = 'Đã bán - Có đổ chuông'
                    sim_state = 'da_ban'
                elif state_value == 'da_ban_khong_chuong':
                    state = 'Đã bán - Không đổ chuông'
                    sim_state = 'da_ban'
                elif state_value == 'da_ban_check_tho':
                    state = 'Đã bán - Check thợ'
                    sim_state = 'da_ban'
                elif state_value == 'da_ban_nang_gia':
                    state = 'Đã bán để nâng giá bán'
                    sim_state = 'da_ban'
                elif state_value == 'da_ban_khach_yeu_cau':
                    state = 'Đã bán khách yêu cầu gỡ bảng'
                    sim_state = 'da_ban'
                elif state_value == 'da_ban_dau_chi_tieu':
                    state = 'Đã bán đấu chỉ tiêu'
                    sim_state = 'da_ban'
                elif state_value == 'sai_gia':
                    state = 'Sai giá'
                    sim_state = ''
                elif state_value == 'da_co_nv_check':
                    state = 'Đã có NV check trước'
                    sim_state = ''
            
            if sim_state:
                if not apply_all:
                    partner.with_user(user_id).write({'sim_status': sim_state})
                else:
                    if sim_state == 'da_ban':
                        partner.sim_data_id.sim_warehouse_ids.with_user(user_id).write({'sim_status': sim_state})

            comment_history = request.env['dth.kho.comment.history'].with_user(user_id).create({
                'sim_warehouse_id': sim_warehouse_id,
                'sim_data_id': sim_data_id,
                'state': state,
                'note': note,
                'apply_all': apply_all
            })
            result = {
                "data": data
            }
            return successful_response(status=200, data=result, success_code='success', message=_("Thêm dữ liệu thành công"))
        except AccessError as a:
            _logger.error(str(a))
            return error_response(status=401, error_code=_("access_error"), message=_("Bạn không có quyền truy cập dữ liệu này"), data={})
        except ValueError as v:
            error_descrip = _("Wrong input format!")
            _logger.error(str(v))
            return error_response(status=400, error_code='value_error', message=error_descrip)
        except Exception as e:
            _logger.error(f"Exception: {str(e)}", exc_info=True)  # Log full exception traceback
            return error_response(status=500, error_code=_("exception_error"), message=_("Đã có lỗi xảy ra. Vui lòng liên hệ quản trị hệ thống."), data={})
