import json
import logging
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
import werkzeug.wrappers

from odoo import http, _
from odoo.exceptions import UserError, ValidationError,AccessError
from odoo.http import request
from odoo.osv import expression
from .main import error_response, successful_response

_logger = logging.getLogger(__name__)

class SimWarehouse(http.Controller):
    @http.route('/api/sim_warehouse/get_list_sim_warehouse',
                methods=['POST'],
                type='http',
                auth='none',
                cors='*',
                csrf=False)
    def get_list_sim_warehouse(self, **kw):
        try:
            user_id = kw.get('user_id', False)
            limit = kw.get('limit', 0)
            page = kw.get('page', 0)
            domain = []
            limit = int(limit)
            page =  int(page)

            # if kw.get('order_by'):
            #     sort = kw.get('order_by')
            if kw.get('key_word', False):
                key_word = kw.get('key_word').strip().replace('.', '')
                domain = expression.AND([domain, [('name', 'ilike', key_word)]])
            if kw.get('min_price', False):
                min_price = int(kw.get('min_price'))
                domain = expression.AND([domain, [('web_price_s', '>=', min_price)]])
            if kw.get('max_price', False):
                max_price = int(kw.get('max_price'))
                domain = expression.AND([domain, [('web_price_s', '<=', max_price)]])
            if kw.get('warehouse_code', False):
                warehouse_code = kw.get('warehouse_code').strip()
                domain = expression.AND([domain, [('sim_maker_id.code', '=', warehouse_code)]])
            if not kw.get('show_sold', False):
                domain = expression.AND([domain, [('sim_status', '!=', 'da_ban')]])
            if kw.get('30days', False):
                domain = expression.AND([domain, [('write_date', '>=', datetime.now() - relativedelta(days=30))]])
            if kw.get('telcom_code', False):
                telcom_code = kw.get('telcom_code', False).split(',')
                domain = expression.AND([domain, [('telecom_supplier_id.code', 'in', telcom_code)]])
            if kw.get('category', False):
                category = kw.get('category', False).split(',')
                domain = expression.AND([domain, [('category_ids.code', 'in', category)]])
            if kw.get('tra_truoc', False) and not kw.get('tra_sau', False):
                domain = expression.AND([domain, [('sub_type', '=', '1')]])
            if kw.get('tra_sau', False) and not kw.get('tra_truoc', False):
                domain = expression.AND([domain, [('sub_type', '=', '0')]])
            if kw.get('avoid_0', False):
                domain = expression.AND([domain, [('num3', '!=', 0), ('num4', '!=', 0), ('num5', '!=', 0), ('num6', '!=', 0), ('num7', '!=', 0), ('num8', '!=', 0), ('num9', '!=', 0)]])
            if kw.get('avoid_1', False):
                domain = expression.AND([domain, [('name', 'not ilike', '1')]])
            if kw.get('avoid_2', False):
                domain = expression.AND([domain, [('name', 'not ilike', '2')]])
            if kw.get('avoid_3', False):
                domain = expression.AND([domain, [('name', 'not ilike', '3')]])
            if kw.get('avoid_4', False):
                domain = expression.AND([domain, [('name', 'not ilike', '4')]])
            if kw.get('avoid_5', False):
                domain = expression.AND([domain, [('name', 'not ilike', '5')]])
            if kw.get('avoid_6', False):
                domain = expression.AND([domain, [('name', 'not ilike', '6')]])
            if kw.get('avoid_7', False):
                domain = expression.AND([domain, [('name', 'not ilike', '7')]])
            if kw.get('avoid_8', False):
                domain = expression.AND([domain, [('name', 'not ilike', '8')]])
            if kw.get('avoid_9', False):
                domain = expression.AND([domain, [('name', 'not ilike', '9')]])
            if kw.get('avoid_49', False):
                domain = expression.AND([domain, [('name', 'not ilike', '49')]])
            if kw.get('avoid_53', False):
                domain = expression.AND([domain, [('name', 'not ilike', '53')]])
                
            dau_so_domain = []
            if kw.get('dau_03', False):
                if not dau_so_domain:
                    dau_so_domain = [('name', '=ilike', '03%')]
                else:
                    dau_so_domain = expression.OR([dau_so_domain, [('name', '=ilike', '03%')]])
            if kw.get('dau_05', False):
                if not dau_so_domain:
                    dau_so_domain = [('name', '=ilike', '05%')]
                else:
                    dau_so_domain = expression.OR([dau_so_domain, [('name', '=ilike', '05%')]])
            if kw.get('dau_07', False):
                if not dau_so_domain:
                    dau_so_domain = [('name', '=ilike', '07%')]
                else:
                    dau_so_domain = expression.OR([dau_so_domain, [('name', '=ilike', '07%')]])
            if kw.get('dau_08', False):
                if not dau_so_domain:
                    dau_so_domain = [('name', '=ilike', '08%')]
                else:
                    dau_so_domain = expression.OR([dau_so_domain, [('name', '=ilike', '08%')]])
            if kw.get('dau_09', False):
                if not dau_so_domain:
                    dau_so_domain = [('name', '=ilike', '09%')]
                else:
                    dau_so_domain = expression.OR([dau_so_domain, [('name', '=ilike', '09%')]])
            if dau_so_domain:
                domain = expression.AND([domain, dau_so_domain])

            total_records = request.env['dth.kho.sim.warehouse'].with_user(user_id).search_count(domain)
            last_page = math.ceil(total_records/limit) or 1
            offset = 0 if limit * (page - 1) < 0 else limit * (page - 1)

            data = []
            sim_warehouses = request.env['dth.kho.sim.warehouse'].with_user(user_id).search_read(domain, fields=['id'], limit=limit, offset=offset)
            if sim_warehouses:
                sql = """
                    WITH last_comments AS (
                         SELECT *
                         FROM dth_kho_comment_history
                         WHERE apply_all = True AND id IN (
                            SELECT MAX(id)
                            FROM dth_kho_comment_history
                            GROUP BY sim_data_id
                        )
                    ),
                    sim_data_with_packages AS (
                        SELECT 
                            sd.id AS sim_data_id,
                            json_agg(json_build_object('name', dkmp.name, 'monthly_fee', dkmp.monthly_fee)) AS packages
                        FROM dth_kho_sim_data AS sd
                        INNER JOIN dth_kho_mobile_package_dth_kho_sim_data_rel dkmpdksdr ON dkmpdksdr.dth_kho_sim_data_id = sd.id
                        INNER JOIN dth_kho_mobile_package dkmp ON dkmp.id = dkmpdksdr.dth_kho_mobile_package_id
                        GROUP BY sd.id
                    )
                        SELECT sw.id AS sim_id,
                            sd.name AS sim_name,
                            sd.name_full AS sim_name_full,
                            sd.web_price_s,
                            sw.sell_price_s,
                            sw.buy_price_s,
                            sw.write_date,
                            sw.sim_status,
                            sd.sub_type,
                            sd.commited,
                            tc.code AS telcom_code,
                            tc.name AS telcom_name,
                            sm.code AS sm_code,
                            sm.name AS sm_name,
                            sm.priority_wh,
                            sm.monopoly_wh,
                            sm.dth_wh,
                            sm.peel_wh,
                            
                            sm.phone_number,
                            sm.email,
                            sm.note AS sm_note,
                            sm.increase_show,
                            sm.hotline_check,
                            cp.name AS province,
                            cm.create_date AS cm_create_date,
                            cm.state AS cm_state,
                            cm.note AS cm_note,
                            us.login AS cm_user_name,
                            sdp.packages
                    FROM dth_kho_sim_warehouse AS sw
                    INNER JOIN dth_kho_sim_data AS sd ON sd.id = sw.sim_data_id
                    INNER JOIN dth_kho_sim_maker AS sm ON sm.id = sw.sim_maker_id
                    LEFT JOIN dth_kho_telecom_supplier AS tc ON tc.id = sd.telecom_supplier_id
                    LEFT JOIN last_comments AS cm ON cm.sim_data_id = sd.id
                    LEFT JOIN res_users AS us ON us.id = cm.create_uid
                    LEFT JOIN res_country_province AS cp ON cp.id = sm.province_id
                    LEFT JOIN sim_data_with_packages AS sdp ON sdp.sim_data_id = sd.id
                    WHERE sw.id IN (%s)
                    ORDER BY sd.id, sw.write_date DESC
                """ % (",".join([str(item['id']) for item in sim_warehouses]),)
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
