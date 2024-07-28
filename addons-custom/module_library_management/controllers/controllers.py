# -*- coding: utf-8 -*-
# from odoo import http


# class ModuleLibraryManagement(http.Controller):
#     @http.route('/module_library_management/module_library_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/module_library_management/module_library_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('module_library_management.listing', {
#             'root': '/module_library_management/module_library_management',
#             'objects': http.request.env['module_library_management.module_library_management'].search([]),
#         })

#     @http.route('/module_library_management/module_library_management/objects/<model("module_library_management.module_library_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('module_library_management.object', {
#             'object': obj
#         })

